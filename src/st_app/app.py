import streamlit as st
from src.st_app import event_loop


# def rh_ops(self):
#     self.gpu = init_rh()
#     if self.gpu:
#         self.query_fn = get_rh_query_fn(get_llm_response, self.gpu)

def render_event_loop():
    ############################################################################################################
    # Initialize the state, this will only happen once - No inputs, the streamlit state is initialized
    ############################################################################################################
    if not st.session_state.get("state_initialized"):
        event_loop.init_st_state()

    ############################################################################################################
    # Create the app base - No inputs other than the UI itself and no outputs are captured
    ############################################################################################################
    event_loop.app_base()

    ############################################################################################################
    # Create the app sidebar
    ############################################################################################################
    #   [INPUT]
    #       1. Front-End UI component to capture their OpenAI API key and provide app usage instructions
    #   [OUTPUT]
    #       1. [optional] A string containing the user's OpenAI API key which is stored as state via st.session_state
    ############################################################################################################
    event_loop.app_sidebar()

    ############################################################################################################
    # Create the file upload widget
    ############################################################################################################
    #   [INPUT]
    #       1. Front-End UI widget that allows for the uploading of a file (restricted to a given file list)
    #   [OUTPUT]
    #       1. [optional] A streamlit object containing the uploaded file which is stored as state via st.session_state
    ############################################################################################################
    event_loop.file_upload()

    ############################################################################################################
    # Enter backend event loop (wrap as a single fn?) - the underlying steps here are cached (data)
    ############################################################################################################
    #   [INPUT]
    #       1. An uploaded file (streamlit object... essentially bytes and some metadata)
    #
    #   [OUTPUT]
    #       1. The entirety of the document text as a single string
    #       2. A vector store to be used for indexing in the future (contains the chunked document text embeddings)
    ############################################################################################################
    if st.session_state["uploaded_file"] is not None and event_loop.check_auth():
        _file = st.session_state["uploaded_file"]
        document_text = event_loop.parse_upload(_file)
        vectorstore = event_loop.embed_document(document_text)

    ############################################################################################################
    # Create the query textbox widget that will capture the user input
    ############################################################################################################
    #   [INPUT]
    #       1. Front-End UI widget that allows for the user to enter a query
    #   [OUTPUT]
    #       1. [optional] A streamlit object containing the user's query which is stored as state via st.session_state
    ############################################################################################################
    event_loop.user_query()

    ############################################################################################################
    # Create the advanced options expansion widget allowing the user to have fine-grained control over the app
    ############################################################################################################
    #
    ##
    event_loop.advanced_options()

    if st.session_state.get("show_full_doc") and st.session_state.get("document_text"):
        event_loop.show_full_doc()

    # Button Press
    event_loop.submit_button()

    # Button Press and All Variables are Acounted For
    if st.session_state.get("submit_state") and event_loop.submit_check():
        event_loop.create_ui_columns()

        sources = event_loop.get_sources_for_context(
            _vs=st.session_state.get("vectorstore"),
            query_text=st.session_state.get("query_text"),
            top_k=st.session_state.get("top_k_sources")
        )

        llm = event_loop.create_llm(
            st.session_state.get("model_name"),
            st.session_state.get("OPENAI_API_KEY"),
            st.session_state.get("model_temperature"),
            st.session_state.get("use_streaming"),
            _container = st.session_state.get("response_box") if st.session_state.get("use_streaming") else None
        )

        # clear the callback text state if using streaming
        if st.session_state.get("use_streaming"):
            llm.callbacks[0].text = ""

        # capture hyperparameters so streamlit knows when something has changed
        hyperparameters = dict(
            model_name=st.session_state.get("model_name"),
            OPENAI_API_KEY=st.session_state.get("OPENAI_API_KEY"),
            model_temperature=st.session_state.get("model_temperature"),
            top_k_sources=st.session_state.get("top_k_sources"),
        )

        raw_llm_response = event_loop.query_llm(
            llm, sources, st.session_state.get("query_text"), hyperparameters
        )
        llm_response, referenced_sources = event_loop.process_raw_llm_response(raw_llm_response, sources)

        event_loop.render_sources(sources if st.session_state.get("show_all_chunks") else referenced_sources)
        event_loop.render_llm_response(llm_response)


    # self.submit()


if __name__ == "__main__":
    render_event_loop()
