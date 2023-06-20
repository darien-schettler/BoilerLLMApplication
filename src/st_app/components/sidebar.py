import os
import streamlit as st

from src import _CONSTANTS
from src.auth import set_openai_api_key, dotenv_auth

# Define the URL to the OpenAI API keys page
OPENAI_API_KEYS_URL = _CONSTANTS.get('OPENAI_API_KEYS_URL', 'www.google.com')

# Define the app description
APP_DESC = _CONSTANTS.get('APP_DESCRIPTION', 'FILL ME IN')


def sidebar():
    """
    Create a sidebar for the Streamlit application.

    The sidebar includes:
      - Instructions on how to use the app.
      - An input field for the user to enter their OpenAI API key.
    """
    with st.sidebar:
        # Display instructions
        st.markdown(
            f"## How to use\n"
            f"1. Type your [OpenAI API key]({OPENAI_API_KEYS_URL}) below\n"
            f"2. Upload a doc (pdf, docx, or txt)\n"
            f"3. Ask some questions!!\n"
        )

        st.divider()

        # Get API key input from the user
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help=f"You can get your API key from {OPENAI_API_KEYS_URL}.",
            value=st.session_state.get("OPENAI_API_KEY", ""),
        )

        if api_key_input:
            set_openai_api_key(api_key_input)
        else:
            dotenv_auth()
            if os.environ["OPENAI_API_KEY"]:
                set_openai_api_key(os.environ["OPENAI_API_KEY"])

        st.divider()

        st.markdown("# About")
        st.markdown(APP_DESC)
