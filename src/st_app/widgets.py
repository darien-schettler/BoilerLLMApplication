import streamlit as st
from typing import List
from src.st_app.state_utils import (
    update_stss,
    reset_submit_state
)


def file_upload_widget(
        default_label: str = "Upload a pdf, docx, or txt file", supported_file_types=None,
        help_text: str = "Scanned documents and multiple files are not supported yet!",
        state_var_name="uploaded_file", **kwargs
):
    """ Uploads a file and parses it into a list of Documents.

    Args:
        default_label (str, optional): The default label for the file upload widget
        supported_file_types (List[str], optional): The list of supported file types
            - pdf, docx, txt
        help_text (str, optional): The help text to display below the file upload widget

    Returns:
        None; Updates the session state with the uploaded file.

    Streamlit State Updates:
        st.session_state['uploaded_file']
            --> contains the uploaded file (SomeUploadedFiles)
    """

    # Enable uploading a file from the list of supported file types (not scanned documents)
    #   --> This is required because we don't like lists as default args
    if supported_file_types is None:
        supported_file_types = ["pdf", "docx", "txt"]

    upload_file_widget_state = st.file_uploader(default_label, type=supported_file_types,
                                                accept_multiple_files=False, help=help_text)

    # Update the state variables
    update_stss(state_var_name, upload_file_widget_state)


def checkbox_widget(label, state_var_name, default_value=False, **kwargs):
    checkbox_widget_state = st.checkbox(label, value=default_value, **kwargs)
    update_stss(state_var_name, checkbox_widget_state)


def slider_widget(label, min_value, max_value, value, step, state_var_name, **kwargs):
    slider_widget_state = st.slider(label, min_value, max_value, value, step, **kwargs)
    update_stss(state_var_name, slider_widget_state)

    # with top_k_col:
#             self.top_k = st.slider(
#                 "How many document chunks to return?",
#                 min_value=1, max_value=20, value=5, step=1, on_change=reset_submit_state
#             )
#         with temp_col:
#             self.temp = st.slider(
#                 "Temperature of the model?",
#                 min_value=0.0, max_value=1.5, value=0.0, step=0.05, on_change=reset_submit_state
#             )


def model_hyperparameter_settings_columns_widget():
    column_widget(column_names=["Model Temperature", "Top K Sources"], n_columns=2)
    with st.session_state.get("Model Temperature"):
        slider_widget(
            "Model Temperature", min_value=0.0, max_value=1.5, value=0.0, step=0.05,
            state_var_name="model_temperature", on_change=reset_submit_state
        )
    with st.session_state.get("Top K Sources"):
        slider_widget(
            "Top K Sources", min_value=1, max_value=10, value=5, step=1,
            state_var_name="top_k_sources", on_change=reset_submit_state
        )


def advanced_options_widget(label="Advanced Options", **kwargs):
    with st.expander(label):
        checkbox_widget("Show all chunks that were injected as context", "show_all_chunks", default_value=False)
        checkbox_widget("Show the entire document after parsing", "show_full_doc", default_value=False)
        checkbox_widget("Stream the model results (Only On Local)", "use_streaming", default_value=False)
        model_hyperparameter_settings_columns_widget()


def show_full_doc_widget(label="Full Document", full_doc_var_name="document_text", **kwargs):
    with st.expander(label):
        st.markdown(st.session_state.get(full_doc_var_name, ""), unsafe_allow_html=True)


def textbox_widget(label, state_var_name, default_value="", return_container=False, **kwargs):
        textbox_widget_state = st.text_area(label, **kwargs)
        update_stss(state_var_name, textbox_widget_state)
        if return_container:
            return textbox_widget_state


def query_textbox_widget(label="Ask a question about the document", **kwargs):
    textbox_widget(label, state_var_name="query_text", return_container=False, on_change=reset_submit_state)


def column_widget(column_names=None, n_columns=2, return_column_names=False, **kwargs):
    if not column_names or len(column_names)!=n_columns:
        column_names = [f"column_{i+1:<02}" for i in range(n_columns)]
        return_column_names=True
    for window_column_name, column_state in zip(column_names, st.columns(n_columns)):
        update_stss(window_column_name, column_state)
    if return_column_names:
        return column_names


def button_widget(label, state_var_name, **kwargs):
    button_widget_state = st.button(label, on_click=reset_submit_state)
    update_stss(state_var_name, button_widget_state)


def llm_response_textbox_widget(label="", **kwargs):
    llm_response_container = textbox_widget(label, state_var_name="response_text", return_container=True)
    return llm_response_container


def empty_widget(state_var_name, **kwargs):
    empty_widget_state = st.empty()
    update_stss(state_var_name, empty_widget_state)
