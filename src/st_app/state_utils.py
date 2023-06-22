import streamlit as st

# @st.cache_data(show_spinner=False)
# The st.cache_data decorator caches the result of this function so that it is
#     only run once per file. This is useful for large files that take a long
#     time to process. `` is required because the
#     Document objects need to be mutable. `show_spinner=False` hides the
#     spinner that Streamlit displays while the function is running.
# If the user has not entered an API key that is stored in state, raise an error
#     if not st.session_state.get("OPENAI_API_KEY"):
#         raise AuthenticationError("👈 Enter your API key in the sidebar (https://platform.openai.com/account/api-keys)")
#     st.session_state.get("OPENAI_API_KEY")


def update_stss(var_name, var_value):
    """ Adds a variable to the session state

    Args:
        var_name (str): The name of the variable to add
        var_value (any): The value of the variable to add

    Returns:
        None; Adds the variable to the session state
    """
    if not st.session_state.get("valid_keys"):
        st.session_state["valid_keys"] = []

    if var_name not in st.session_state["valid_keys"]:
        st.session_state["valid_keys"].append(var_name)
        st.session_state[var_name] = var_value
    else:
        st.session_state[var_name] = var_value


def reset_submit_state(submit_state_var_name="submit_state"):
    """ Clears the submit button """
    st.session_state[submit_state_var_name] = False


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
        update_stss("OPENAI_API_KEY", api_key)
