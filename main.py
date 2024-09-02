# Create streamlit app

import streamlit as st
from model import ChatBot
import requests

chatbot = ChatBot()
 
# configure web page
st.set_page_config(page_title="QuaLLM.ai", page_icon="✨", layout="wide")

# initialise session state for tracking user input and responses
if 'responses' not in st.session_state:
    st.session_state.responses = []

def scroll_to_bottom_of_page():
    """ Return focus to bottom of page once a question is entered."""
    # Define the scroll operation as a function and pass in something unique for each
    # page load that it needs to re-evaluate where "bottom" is
    js = f"""
    <script>
        function scroll(dummy_var_to_force_repeat_execution){{
            var textAreas = parent.document.querySelectorAll('section.main');
            for (let index = 0; index < textAreas.length; index++) {{
                textAreas[index].scrollTop = textAreas[index].scrollHeight;
            }}
        }}
        scroll({len(st.session_state.responses)})
    </script>
    """

    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        console.log(body);
        body.scrollTop = 0;
    </script>
    '''
    st.components.v1.html(js)

def display_chat_history():
    with st.container():
        for response in st.session_state.responses:
            left, right = st.columns(2)
            right.markdown(f"""
                <div style="background-color:#262730; padding:10px; border-radius:20px;">
                    <p style="font-family:Arial, sans-serif; font-color: #2f2f2f; ">{response['user']}</p>
                </div>
                </br>
                """, 
                unsafe_allow_html=True,
            )
            st.empty().markdown(f"""
                <div style="padding:10px; border-radius:5px;">
                    <p style="font-family:Arial, sans-serif; font-color: #2f2f2f; ">{response['bot']}</p>
                </div>
                </br>
                """, 
                unsafe_allow_html=True,
            )

def post_request_to_api(url: str, message: str, model: str, temperature: float, max_tokens: str):
    """Send the user input to backend API"""
    response = requests.post(
        url,
        json={
            "message": message,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        },
        stream=True,
    )
    return response

def handle_message(user_input, backend_url, selected_model, set_tokens, temperature, selected_response_type): # default selection is Stream
    if user_input:
        # add user input to session state
        st.session_state.responses.append({'user': user_input, 'bot': None})

        response = post_request_to_api(
            url=backend_url,
            message=user_input,
            model=selected_model,
            temperature=temperature,
            max_tokens=set_tokens,
        )

        # prepare empty container to update the bot's response in real time
        response_container = st.empty()

        if response.status_code == 200:
            bot_response = ""
            if selected_response_type == chatbot.output_type[0]:
                # stream response from backend
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    bot_response += chunk
                    # update response container with the latest bot response
                    response_container.markdown(
                        f"""
                        <div style="padding:10px; border-radius: 5px;">
                            <p style="font-family: Arial, sans-serif; font-color: #2f2f2f">{bot_response.strip()}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # update the latest bot response in session state
                    st.session_state.responses[-1]['bot'] = bot_response.strip()

            else:
                # collect the batch response
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    bot_response += chunk
                
                # display bot's response with adaptable height
                st.markdown(
                    f"""
                    <div style="padding:10px; border-radius: 5px;">
                        <p style="font-family: Arial, sans-serif; font-color: #2f2f2f">{bot_response.strip()}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            # update the latest bot response in session state
            st.session_state.responses[-1]['bot'] = bot_response.strip()

        else:
            response_container.markdown(
                "<p style='color:red;'>Error: Unable to get a response from the server.</p>", 
                unsafe_allow_html=True,
            )
        # clear input box for next question
        # st.session_state.current_input = ""

def get_configs():
    with st.sidebar:
        expander = st.expander("Select your response type", expanded=True)
        with expander:
            selected_response_type = st.radio("Output types", chatbot.output_type, index=None)
        # select model and training parameters
        selected_model = st.selectbox("Select your preferred model: ", chatbot.models)
        temperature = st.number_input(
            "Enter the parameter for model temperature (Number must be a float between 0 and 2)", 
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            format="%.1f"
        )
        set_tokens = st.selectbox("Please select length of output", chatbot.token_class.keys())
        return selected_model, selected_response_type, temperature, set_tokens

# main layout
def main():
    scroll_to_bottom_of_page()
    display_chat_history()

    selected_model, selected_response_type, temperature, set_tokens = get_configs()
    selected_response_type = selected_response_type if selected_response_type else chatbot.output_type[0] # default selection is Stream 
    # collect user input below the chat history
    prompt = st.chat_input("Ask a question")
    if prompt:
        user_input = prompt

        # define the URL of the backend API
        if selected_response_type == chatbot.output_type[0]:
            backend_url = "http://127.0.0.1:5000/chat_stream"
        else:
            backend_url = "http://127.0.0.1:5000/chat_batch"
        
        if user_input:
            left, right = st.columns(2)
            right.markdown(f"""
            <div style="background-color:#262730; padding:10px; bottom-margin: 1px; border-radius:20px;">
                <p style="font-family:Arial, sans-serif; font-color: #2f2f2f; ">{user_input}</p>
            </div>
            </br>
            """, 
            unsafe_allow_html=True)
            handle_message(
                user_input=user_input,
                backend_url=backend_url,
                selected_response_type=selected_response_type,
                selected_model=selected_model,
                set_tokens=set_tokens,
                temperature=temperature,
            )

if __name__ =="__main__":
    main()