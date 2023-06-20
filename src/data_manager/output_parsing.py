from typing import List, Union, Dict, Any, Tuple
import streamlit as st

# LANGCHAIN
from langchain.docstore.document import Document


def wrap_text_in_html(text: Union[str, List[str]]) -> str:
    """ Wraps each text block separated by newlines in <p> tags so that it can be displayed in Streamlit.

    Args:
        text (Union[str, List[str]]): A string or list of strings to wrap in <p> tags

    Returns:
        str: A string with each text block wrapped in <p> tags
    """

    # Add horizontal rules between pages (coercion)
    if isinstance(text, list): text = "\n<hr/>\n".join(text)

    # Wrap each line in <p> tags
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])


@st.cache_data()
def llm_response_w_sources(
        raw_response: Dict[str, Any],
        _docs: List[Document],
        return_llm_response: bool = True
) -> Union[List[Document], Tuple[List[Document], str]]:
    """ Parses the model's response and returns source information (and optionally the model's response)

    The st.cache_data decorator caches the result of this function so that it is
    only run once per file. This is useful for large files that take a long
    time to process. `` is required because the
    input arguments need to be mutable.

    Args:
        raw_response (Dict[str, Any]): A dictionary containing the raw LLM response and the source Documents.
        _docs (List[Document]): A list of Documents that have been chunked w/ appropriate metadata.
        return_llm_response (bool, optional): Whether to return only sources or include the LLM response as well

    Returns:
        List[Document]: A list of Documents that are the sources for the answer.
    """
    response_split = raw_response["output_text"].split("SOURCES: ")
    llm_response, sources = response_split[0], "".join(response_split[1:])

    source_keys = [x.strip() for x in sources.split(",")]
    source_docs = [doc for doc in _docs if doc.metadata["source"] in source_keys]

    if return_llm_response:
        return source_docs, llm_response
    else:
        return source_docs

