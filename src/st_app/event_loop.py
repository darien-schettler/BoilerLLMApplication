"""
This file contains the function wrappers that abstract code into the event loop for the streamlit app that will
be run on every detected change. Due to this, some of the code may simply be a pass through for the underlying code
or widget. This is done to ensure that the code is run on every change and that the state is updated accordingly.

Generally the code in the event loop does 1 of 3 things:
    1. Initialize something
    2. Check the state of something (widget, component, etc.)
    3. Execute some backend code
"""

import os
import streamlit as st
from src.st_app.widgets import (
    file_upload_widget,
    query_textbox_widget,
    llm_response_textbox_widget,
    advanced_options_widget,
    show_full_doc_widget,
    button_widget,
    column_widget,
    empty_widget
)
from src.st_app.components import (
    sidebar,
)
from src.st_app.state_utils import (
    update_stss,
    reset_submit_state,
    set_openai_api_key
)
from src.model_manager.model_ecosystem import (
    get_openai_model,
    get_llm_response
)

from src.st_app.widgets import (
    file_upload_widget,
)
from src.data_manager.data_loader import (
    parse_document,
    embed_text,
    search_docs
)
from src.data_manager.output_parsing import (
    split_raw_llm_response,
)
def init_st_state():
    """ Initializes the streamlit app

    Args:
        page_title (str, optional): The title of the page
        page_icon (str, optional): The icon to use for the page
        layout (str, optional): The layout of the page

    Returns:
        None; Initializes the streamlit app
    """

    # Initialize some state defaults and add to global config
    for stss_key in [
        'uploaded_file', 'vectorstore', 'document_text',
        'query_text', 'show_full_doc', 'show_all_chunks',
        'submit_state', 'openai_api_key', 'llm_response'
    ]:
        update_stss(stss_key, None)
    update_stss("query_fn", get_llm_response)
    update_stss("model_name", "gpt-3.5-turbo-0613")
    update_stss("state_initialized", True)


def app_base(page_title="BoilerLLM", page_icon="📖", layout="wide"):
    # Initialize the page config (set's the layout width as well)
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

    # Initialize the header string
    st.header(f"{page_icon} {page_title}")


def app_sidebar():
    # Initialize the sidebar
    sidebar.sidebar()


def file_upload(**file_upload_widget_kwargs):
    file_upload_widget(**file_upload_widget_kwargs)


@st.cache_data()
def parse_upload(file):
    """ Parses the uploaded file into a str """

    # If a file is uploaded, parse it into a list of Documents
    #  - If the file is a pdf, use `pypdf.PdfReader` to extract the text
    #  - If the file is a docx, use `docx2txt.process` to extract the text
    #  - If the file is a txt, use built-ins and `re` to extract the text
    #  - If the file is not one of the above, raise a `ValueError`
    document_text = parse_document(f_bytes=file, f_name=file.name)
    update_stss("document_text", document_text)
    return document_text


def check_auth(api_key="OPENAI_API_KEY"):
    """ Before moving forward we need to check auth """
    if st.session_state.get(api_key):
        return True
    env_key = os.environ.get(api_key)
    if env_key:
        set_openai_api_key(env_key)
        return True
    else:
        st.error("Please configure your OpenAI API key!")
        return False


# TODO: Add a decorator for st that catches relevant errors and displays them?
@st.cache_data()
def embed_document(document_text):
    """ If the file is successfully parsed, embed the text into a vector index """
    vectorstore = embed_text(document_text, openai_api_key=st.session_state["OPENAI_API_KEY"])
    update_stss("vectorstore", vectorstore)
    return vectorstore


def user_query(**query_widget_kwargs):
    """ Capture the query from the user using `st.text_area` """
    query_textbox_widget()


def advanced_options(**advanced_options_widget_kwargs):
    advanced_options_widget(**advanced_options_widget_kwargs)


def show_full_doc(**full_doc_widget_kwargs):
    show_full_doc_widget(**full_doc_widget_kwargs)


def submit_button():
    """ The submit button that will run the query """
    button_widget("SUBMIT", state_var_name="submit_state")


def submit_check():
    """ Checks that all the required state variables are set """

    reset_flag = False
    if not st.session_state.get("OPENAI_API_KEY"):
        st.error("Please configure your OpenAI API key!")
    if not st.session_state.get("uploaded_file"):
        st.error("Please upload a document!")
    if not st.session_state.get("query_text"):
        st.error("Please enter a question!")

    if reset_flag:
        reset_submit_state()
        return False
    else:
        return True


def update_ui_column(column_name, response_box=False, **kwargs):
    """ Updates the ui split column with the UI elements """
    column_state_container = st.session_state.get(column_name)
    with column_state_container:
        st.markdown(f"#### {column_name}")
        if response_box:
            empty_widget("response_box", **kwargs)


def create_ui_columns(left_column_name="LLM Response",
                      right_column_name="Sources",
                      **window_column_widget_kwargs):
    column_names = [left_column_name, right_column_name]
    column_widget(column_names=column_names, n_columns=len(column_names), **window_column_widget_kwargs)
    update_ui_column(left_column_name, response_box=True)
    update_ui_column(right_column_name, response_box=False)
    return column_names


@st.cache_data()
def get_sources_for_context(_vs, query_text, top_k=5, **kwargs):
    sources = search_docs(vectorstore=_vs, query=query_text, top_k=top_k)
    return sources


@st.cache_resource()
def create_llm(model_name, openai_api_key, model_temperature=0.0, use_streaming=False, _container=None):
    if _container: _container.text=""
    llm = get_openai_model(
        model_name=model_name,
        temperature=model_temperature,
        use_streaming=use_streaming,
        st_container=_container,
        openai_api_key=openai_api_key)
    return llm


@st.cache_data()
def query_llm(_llm, _sources, query_text, hyperparameters):
    """ Gets the LLM response for the query """
    llm_response = st.session_state.get("query_fn")(_llm, _sources, query_text, hyperparameters)["output_text"]
    update_stss("raw_llm_response_text", llm_response)
    return llm_response


@st.cache_data()
def process_raw_llm_response(raw_llm_response, _sources):
    llm_response, referenced_sources = split_raw_llm_response(
        raw_llm_response, top_k_sources=_sources, return_llm_response=True
    )
    update_stss("llm_response_text", llm_response)
    update_stss("llm_response_references", referenced_sources)
    return llm_response, referenced_sources


def render_sources(sources, source_state_var="Sources"):
    """ Renders the LLM response in the UI """

    with st.session_state.get(source_state_var):
        for source in sources:
            with st.expander(source.metadata["source"]):
                st.markdown(source.page_content, unsafe_allow_html=True)
            st.divider()


def render_llm_response(llm_response, llm_response_box_state_var="response_box"):
    """ Renders the LLM response in the UI """

    with st.session_state.get(llm_response_box_state_var):
        st.markdown(llm_response, unsafe_allow_html=True)



#
#     # ----- STEP 2 -----
#     #
#     # Under the 'Advanced Options' expansion panel, monitor two boolean checkboxes
#
#
#         top_k_col, temp_col = st.columns(2)
#         with top_k_col:
#             self.top_k = st.slider(
#                 "How many document chunks to return?",
#                 min_value=1, max_value=20, value=5, step=1, on_change=reset_submit_state
#             )
#         with temp_col:
#             self.temp = st.slider(
#                 "Temperature of the model?",
#                 min_value=0.0, max_value=1.5, value=0.0, step=0.05, on_change=reset_submit_state
#             )
#
#     # ----- STEP 3 -----
#     #
#     # If the user has checked the 'Show parsed contents of the document' checkbox, show the parsed document
#     if self.show_full_doc and self.doc:
#         # Create an expandable area to show the parsed document
#         with st.expander("Document"):
#             # Use `wrap_text_in_html` to wrap the text in html `p` tags to allow it to be rendered in st.markdown
#             st.markdown(f"<p>{wrap_text_in_html(self.doc)}</p>", unsafe_allow_html=True)
#
# def submit(self):
#     """ The code to run if the user presses `submit`
#
#     This will capture the query, identify relevant chunks of text from the document vector store,
#     and will then inject this context along with the parsed query into the LLM. Finally we will return
#     the LLM response as well as the relevant chunks of text from the document vector store as sources
#     """
#
#     # Capture the state of the submit button
#     self.button = st.button("Submit")
#
#     # ----- STEP 1 -----
#     #
#     # If submitted, check the following conditions before proceeding (OpenAI Key, Valid Document, Valid Query)
#     # each of which will be stored as an attribute and will be accessible. If any of these conditions are not met,
#     # display an error message using `st.error` with the respective error message
#     if self.button or st.session_state.get("submit"):
#         if not st.session_state.get("api_key_configured"):
#             st.error("Please configure your OpenAI API key!")
#         elif not self.index:
#             st.error("Please upload a document!")
#         elif not self.query:
#             st.error("Please enter a question!")
#
#         # ----- STEP 2 -----
#         #
#         # If all conditions are met, retrieve the relevant chunks of text from the document vector store
#         #   - Use `search_docs` to retrieve the relevant chunks of text from the document vector store
#         st.session_state["submit"] = True
#         answer_col, sources_col = st.columns(2)
#         with answer_col:
#             st.markdown("#### Answer")
#             self.response_box = st.empty()
#         with sources_col:
#             st.markdown("#### Sources")
#
#         sources = search_docs(self.index, self.query, top_k=self.top_k)
#
#         # Try/Except pass through for OpenAI errors
#         try:
#
#             # ----- STEP 3 -----
#             #
#             # Pass the context and query to the model via `get_answer` and store the response
#             raw_llm_response = self.query_fn(
#                 sources, self.query, use_streaming=self.use_streaming, qa_model_temp=self.temp,
#                 _container=self.response_box if self.use_streaming else None
#             )
#
#             # ----- STEP 4 -----
#             #
#             # If the user wants to see all the injected context in full, we don't retrieve the source strings
#             # as that would be redundant
#             if not self.show_all_chunks:
#                 sources, llm_response = llm_response_w_sources(raw_llm_response, sources, return_llm_response=True)
#             else:
#                 llm_response = raw_llm_response["output_text"].split("SOURCES: ", 1)[0]
#
#             # ----- STEP 5 -----
#             #
#             # Display the answer and sources in the Streamlit UI
#             #  - The output text will have the LLM's response to the LEFT/BEFORE the text 'SOURCES: '
#             #  - The output text will have all the sources to the RIGHT/AFTER the text 'SOURCES: '
#             if not self.use_streaming:
#                 with answer_col:
#                     st.markdown(llm_response, unsafe_allow_html=True)
#
#             with sources_col:
#                 for source in sources:
#                     st.markdown(source.page_content, unsafe_allow_html=True)
#                     st.markdown(source.metadata["source"], unsafe_allow_html=True)
#                     st.divider()
#
#         except OpenAIError as e:
#             st.error(e._message)