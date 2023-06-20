import streamlit as st
from openai.error import OpenAIError
import runhouse as rh

from src.data_manager.data_loader import (
    embed_text,
    parse_docx,
    parse_pdf,
    parse_txt,
    search_docs,
)
from src.data_manager.output_parsing import (
    wrap_text_in_html,
    llm_response_w_sources,
)
from src.model_manager.model_ecosystem import get_llm_response
from src.st_app.components.sidebar import sidebar
from src.runhouse_ops.instance_handler import get_rh_query_fn, init_rh


def clear_submit():
    """ Clears the submit button """
    st.session_state["submit"] = False


class BoilerLLMApp:
    def __init__(self):
        st.set_page_config(page_title="BoilerLLM", page_icon="📖", layout="wide")

        # Initialize the sidebar
        sidebar()

        # Default query fn
        self.query_fn = get_llm_response

        # Initialize the main content
        st.header("📖BoilerLLM")
        self.uploaded_file = None
        self.index = None
        self.doc = None
        self.show_full_doc = False
        self.show_all_chunks = False

    def upload_file(self):
        """ Uploads a file and parses it into a list of Documents """

        # Enable uploading a file from the list of supported file types (not scanned documents)
        self.uploaded_file = st.file_uploader(
            "Upload a pdf, docx, or txt file",
            type=["pdf", "docx", "txt"],
            help="Scanned documents are not supported yet!",
            on_change=clear_submit,
        )

        # ----- STEP 1 -----
        #
        # If a file is uploaded, parse it into a list of Documents
        #  - If the file is a pdf, use `pypdf.PdfReader` to extract the text
        #  - If the file is a docx, use `docx2txt.process` to extract the text
        #  - If the file is a txt, use built-ins and `re` to extract the text
        #  - If the file is not one of the above, raise a `ValueError`
        if self.uploaded_file is not None:
            if self.uploaded_file.name.endswith(".pdf"):
                self.doc = parse_pdf(self.uploaded_file)
            elif self.uploaded_file.name.endswith(".docx"):
                self.doc = parse_docx(self.uploaded_file)
            elif self.uploaded_file.name.endswith(".txt"):
                self.doc = parse_txt(self.uploaded_file)
            else:
                raise ValueError("File type not supported!")

            # ----- STEP 2 -----
            #
            # If the file is successfully parsed, embed the text into a vector index
            #   - Use `embed_docs` to embed the text into a vector index (use spinner in st to show progress)
            #   - If the API key is invalid, raise an `OpenAIError`
            try:
                with st.spinner("Indexing document... This may take a while⏳"):
                    self.index = embed_text(self.doc)
                st.session_state["api_key_configured"] = True
            except OpenAIError as e:
                st.error(e._message)

    def query(self):
        """ Takes a query and returns an answer and sources """

        # ----- STEP 1 -----
        #
        # Capture the query from the user using `st.text_area`
        #   - Use `on_change` to clear the submit state (set to False i.e. startover)
        self.query = st.text_area("Ask a question about the document", on_change=clear_submit)

        # ----- STEP 2 -----
        #
        # Under the 'Advanced Options' expansion panel, monitor two boolean checkboxes
        with st.expander("Advanced Options"):
            self.show_all_chunks = st.checkbox("Show all chunks retrieved from vector search", value=False)
            self.show_full_doc = st.checkbox("Show parsed contents of the document", value=False)
            self.use_streaming = st.checkbox("Stream the model results", value=False)

            top_k_col, temp_col = st.columns(2)
            with top_k_col:
                self.top_k = st.slider(
                    "How many document chunks to return?",
                    min_value=1, max_value=20, value=5, step=1, on_change=clear_submit
                )
            with temp_col:
                self.temp = st.slider(
                    "Temperature of the model?",
                    min_value=0.0, max_value=1.5, value=0.0, step=0.05, on_change=clear_submit
                )

        # ----- STEP 3 -----
        #
        # If the user has checked the 'Show parsed contents of the document' checkbox, show the parsed document
        if self.show_full_doc and self.doc:
            # Create an expandable area to show the parsed document
            with st.expander("Document"):
                # Use `wrap_text_in_html` to wrap the text in html `p` tags to allow it to be rendered in st.markdown
                st.markdown(f"<p>{wrap_text_in_html(self.doc)}</p>", unsafe_allow_html=True)

    def submit(self):
        """ The code to run if the user presses `submit`

        This will capture the query, identify relevant chunks of text from the document vector store,
        and will then inject this context along with the parsed query into the LLM. Finally we will return
        the LLM response as well as the relevant chunks of text from the document vector store as sources
        """

        # Capture the state of the submit button
        self.button = st.button("Submit")

        # ----- STEP 1 -----
        #
        # If submitted, check the following conditions before proceeding (OpenAI Key, Valid Document, Valid Query)
        # each of which will be stored as an attribute and will be accessible. If any of these conditions are not met,
        # display an error message using `st.error` with the respective error message
        if self.button or st.session_state.get("submit"):
            if not st.session_state.get("api_key_configured"):
                st.error("Please configure your OpenAI API key!")
            elif not self.index:
                st.error("Please upload a document!")
            elif not self.query:
                st.error("Please enter a question!")

            # ----- STEP 2 -----
            #
            # If all conditions are met, retrieve the relevant chunks of text from the document vector store
            #   - Use `search_docs` to retrieve the relevant chunks of text from the document vector store
            st.session_state["submit"] = True
            answer_col, sources_col = st.columns(2)
            with answer_col:
                st.markdown("#### Answer")
                self.response_box = st.empty()
            with sources_col:
                st.markdown("#### Sources")

            sources = search_docs(self.index, self.query, top_k=self.top_k)

            # Try/Except pass through for OpenAI errors
            try:

                # ----- STEP 3 -----
                #
                # Pass the context and query to the model via `get_answer` and store the response
                raw_llm_response = self.query_fn(
                    sources, self.query, use_streaming=self.use_streaming, qa_model_temp=self.temp,
                    _container=self.response_box if self.use_streaming else None
                )

                # ----- STEP 4 -----
                #
                # If the user wants to see all the injected context in full, we don't retrieve the source strings
                # as that would be redundant
                if not self.show_all_chunks:
                    sources, llm_response = llm_response_w_sources(raw_llm_response, sources, return_llm_response=True)
                else:
                    llm_response = raw_llm_response["output_text"].split("SOURCES: ", 1)[0]

                # ----- STEP 5 -----
                #
                # Display the answer and sources in the Streamlit UI
                #  - The output text will have the LLM's response to the LEFT/BEFORE the text 'SOURCES: '
                #  - The output text will have all the sources to the RIGHT/AFTER the text 'SOURCES: '
                if not self.use_streaming:
                    with answer_col:
                        st.markdown(llm_response, unsafe_allow_html=True)

                with sources_col:
                    for source in sources:
                        st.markdown(source.page_content, unsafe_allow_html=True)
                        st.markdown(source.metadata["source"], unsafe_allow_html=True)
                        st.divider()

            except OpenAIError as e:
                st.error(e._message)


    def rh_ops(self):
        self.gpu = init_rh()
        if self.gpu:
            self.query_fn = get_rh_query_fn(get_llm_response, self.gpu)

    def render(self):
        self.rh_ops()
        self.upload_file()
        self.query()
        self.submit()

BoilerLLMApp().render()