from src.model_manager.model_loader import get_openai_chat_model
from src.auth import dotenv_auth
import runhouse as rh
import streamlit as st

def get_paperspace_kwargs():
    """ Returns the kwargs for paperspace. """
    return dict(
        ips=["172.83.15.60", ],
        name='my_a100_80g',
        ssh_creds={'ssh_user': 'paperspace', 'ssh_private_key': '~/.ssh/id_rsa'}
    )


@st.cache_resource
def init_rh(kwarg_overrides=None, restart_server=False):
    byos_model_kwargs = get_paperspace_kwargs()

    # Step 3 - Create RH gpu and function for model query
    gpu = rh.cluster(**byos_model_kwargs)
    if restart_server:
        gpu.restart_server()

    return gpu


@st.cache_resource
def get_rh_query_fn(_query_fn, _rh_gpu, env_vars=None):
    return rh.function(_query_fn).to(_rh_gpu, env=env_vars)

def query_model(query, model_type="openai", model_kwargs=None, **kwargs):
    """ Queries the model for a response.

    Args:
        query (list of Messages): The query to send to the model.
        model_type (str, optional): The type of model to use. Defaults to "openai".
        model_kwargs (dict, optional): Additional kwargs to pass to the model. Defaults to None.
        **kwargs: Additional kwargs to pass to the model.

    Returns:
        Response from model based on query, model kwargs and model details
    """
    dotenv_auth()

    # ['hf', 'openai', 'anthropic', 'ai21', 'other']
    model_kwargs = {} if model_kwargs is None else model_kwargs
    model, response = None, None
    if model_type == "openai":
        model = get_openai_chat_model(**model_kwargs)
        response = model(query)
    elif model_type == "hf":
        raise NotImplementedError
    elif model_type == "anthropic":
        raise NotImplementedError
    elif model_type == "ai21":
        raise NotImplementedError
    return response
