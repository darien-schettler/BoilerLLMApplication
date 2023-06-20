from dotenv import load_dotenv, find_dotenv
import streamlit as st


def set_openai_api_key(api_key: str):
    """
    Set the OpenAI API key in the current session state.

    Args:
        api_key (str): The OpenAI API key provided by the user.

    Raises:
        Streamlit error: If the provided API key is invalid (e.g. does not start with "sk-" or is too short)
    """

    # Check if the provided API key is in the expected format
    if not api_key.startswith("sk-"):
        st.error("Invalid OpenAI API key. It should start with 'sk-'.")
        return None
    # Further checks can be added here, like checking the length of the API key
    elif len(api_key) < 20:  # Modify this as per the typical length of an OpenAI API key
        st.error("Invalid OpenAI API key. The provided key is too short.")
        return None
    else:
        # Set the API key in the session state
        st.session_state["OPENAI_API_KEY"] = api_key


def dotenv_auth():
    """ Load .env file for authentication """
    try:
        load_dotenv(find_dotenv())
    except FileNotFoundError:
        print("\n\nPlease upload your .env file to the local directory\n")