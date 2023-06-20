import streamlit as st
def init_stui(subheader="Basic LLM Chatbot - Demo", streaming_pills=True, user_id="You",
              input_text_box_placeholder="Type your query here ...", input_text_box_key="input",
              allow_model_input=True, model_text_box_placeholder="Model name goes here ... i.e. gpt-3.5-turbo-0613",
              model_text_box_key="model_name", **kwargs):

    """ Initialize the Streamlit UI for the LLM Chatbot """
    st.subheader(subheader)

    model_text_box = None
    if allow_model_input:
        model_text_box = st.text_input(f"Model Name:", placeholder=model_text_box_placeholder, key=model_text_box_key)
    else:
        raise NotImplementedError

    is_streaming = lambda: False
    if streaming_pills:
        no_stream_str, yes_stream_str = "NO STREAMING", "YES STREAMING"
        is_streaming = lambda: pills("", [no_stream_str, yes_stream_str], ["🧱", "🌊"])==yes_stream_str

    input_text_box = st.text_input(f"{user_id}: ", placeholder=input_text_box_placeholder, key=input_text_box_key)
    return locals()


def update_stui(model_query_fn, state_kwargs):

    # Get user query from input text box
    bad_query_response = "Please type the following: 'No Input Detected - Please Try Again' immediately following this:"
    user_query = [HumanMessage(content=state_kwargs.get("input_text_box", bad_query_response))]

    # Create top horizontal line
    st.markdown("----")

    # Initialize a box to display the response (starts empty)
    response_box = st.empty()

    # Get model response from model query function and user query
    response = model_query_fn(user_query).content

    # Update the response box with the response
    if not state_kwargs.get("is_streaming", lambda: False)():
        response_box.markdown(f'{response}')
        response_box.write(response)

    # Create bottom horizontal line
    st.markdown("----")

    return locals()


if __name__ == "__main__":

    # Step 1 - Authenticate
    # dotenv_auth()

    # Step 2 - Get BYOServer Model Server Kwargs
    byos_model_kwargs = get_paperspace_kwargs()

    # Step 3 - Create RH gpu and function for model query
    gpu = rh.cluster(**byos_model_kwargs)
    model_query_fn = rh.function(query_model).to(gpu, env=["openai"])

    # Step 4 - Create Initial State for Streamlit UI
    stui_state_vars = init_stui()

    # Step 5 - Catch submit
    if st.button("SUBMIT", type="primary"):
        stui_state_vars = update_stui(model_query_fn, stui_state_vars)

        # EXCEPT:
        ### print("Restarting server and trying again")
        ### gpu.restart_server()
        ### model_query_fn = rh.function(query_model).to(gpu, env=["langchain"])
        ### stui_state_vars = update_stui(model_query_fn, stui_state_vars)
