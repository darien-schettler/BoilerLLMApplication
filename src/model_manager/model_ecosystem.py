import streamlit as st
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from typing import Any, Dict, List, Union
from langchain.docstore.document import Document
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.callbacks.streaming_stdout import BaseCallbackHandler, StreamingStdOutCallbackHandler
from src.prompts import IR_PROMPTS


class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text="", display_method='markdown'):
        self.container = container
        self.text = initial_text
        self.display_method = display_method

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        display_function = getattr(self.container, self.display_method, None)
        if display_function is not None:
            display_function(self.text, unsafe_allow_html=True)
        else:
            raise ValueError(f"Invalid display_method: {self.display_method}")

def get_openai_model(model_name="gpt-3.5-turbo-0613", temperature=0.7, use_streaming=False,
                     streaming_cb="streamlit", st_container=None, verbose=True, **kwargs):
    """
    ["gpt-3.5-turbo-16", "gpt-3.5-turbo-0613"]
    ["streamlit", "stdout"]
    """
    if streaming_cb == "stdout" and use_streaming:
        streaming_cb = [StreamingStdOutCallbackHandler()]
    elif streaming_cb == "streamlit" and use_streaming:
        streaming_cb = [StreamlitCallbackHandler(st_container)]
    else:
        streaming_cb = None

    if "gpt" in model_name:
        model = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            verbose=verbose,
            streaming=use_streaming,
            callbacks=streaming_cb,
            **kwargs
        )
    else:
        model = OpenAI(
            model_name=model_name,
            temperature=temperature,
            verbose=verbose,
            streaming=use_streaming,
            callbacks=streaming_cb,
            **kwargs
        )
    return model


@st.cache_data()
def get_llm_response(
        _docs: List[Document],
        query: str,
        qa_model_name: str = "gpt-3.5-turbo-0613",
        qa_model_temp: Union[float, int] = 0.0,
        qa_chain_type: str = "stuff",
        use_streaming: bool = False,
        _container: st.container = None,
) -> Dict[str, Any]:
    """Gets the LLM response to a question w/ injected context via a list of Documents.

    The st.cache decorator caches the result of this function so that it is
    only run once per file. This is useful for large files that take a long
    time to process. `` is required because the
    input arguments need to be mutable.

    Args:
        _docs (List[Document]):
            - A list of Documents that have been chunked w/ appropriate metadata for which we will extract the most
              relevant results to inject as context into the chat model.
        query (str):
            - The query that we want to answer using the chat model with Documents as context.
        qa_model_name (str, optional):
            - The name of the openai chat model to use
        qa_model_temp (Union[float, int], optional):
            - The temperature to use for the chat model. Lower values are more conservative and deterministic while
              higher values are more creative and unpredictable
        qa_chain_type (str, optional):
            - The type of chain to use for the chat model. Can be ['stuff' | 'reduce' |'rerank']
                - 'stuff' tbd
                - 'reduce' tbd
                - 'rerank' tbd
        use_streaming (bool, optional):
            - Whether to use streaming or not. Defaults to False.
        _container (st.container, optional):
            - The streamlit container to use for streaming. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing the answer and the source Documents.
    """

    # TODO: Replace with our own qa w/ sources chain
    qa_w_srcs_chain = load_qa_with_sources_chain(
        llm = get_openai_model(
            model_name=qa_model_name,
            temperature=qa_model_temp,
            use_streaming=use_streaming,
            streaming_cb="streamlit",
            st_container=_container,
            verbose=True,
            openai_api_key=st.session_state.get("OPENAI_API_KEY")),
        chain_type=qa_chain_type,
        prompt=IR_PROMPTS.get(qa_chain_type),
    )

    # Get the answer by running the chain
    answer = qa_w_srcs_chain({"input_documents": _docs, "question": query}, return_only_outputs=True)
    return answer
