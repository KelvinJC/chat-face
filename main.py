# Create streamlit app

import streamlit as st
from model import ChatBot
import requests

chatbot = ChatBot()

# initialise session state for tracking user input and responses
if 'responses' not in st.session_state:
    st.session_state.responses = []

# # select model and training parameters
# selected_model = chatbot.models[0]
# temperature = 1.5

# # define url of backend chat API
# backend_url = "http://127.0.0.1:5000/chat_batch"

# # handle sending requests and receiving responses
# def handle_message(user_input):
#     if user_input:
#         # add user input to session state
#         st.session_state.responses.append({'user': user_input, 'bot': None})

#         # prepare empty container to update the bot's response in real time
#         response_container = st.empty()

#         # send the user input to backend
#         response = requests.post(
#             backend_url, 
#             json={
#                 "message": user_input,
#                 "model": selected_model,
#                 "temperature": temperature,
#             },
#             stream=True
#         )
#         if response.status_code == 200:
#             bot_response = ""

#             # collect the batch response
#             for chunk in response.iter_content(chunk_size=None, decode_unicode=True):   
#                 bot_response += chunk

#             # display bot response with adaptable height
#             st.markdown("Sharwie:")
#             st.markdown(
#                 f"""
#                 <div style="background-color:#262730; padding:10px; border-radius: 5px;">
#                     <p style="font-family: Arial, sans-serif; font-color: #2f2f2f">{bot_response.strip()}</p>
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )
#         else:
#             response_container.markdown(
#                 "<p style='color: red;'>Error: Unable to get response from server.</p>",
#                 unsafe_allow_html=True,
#             )

def handle_message(
    user_input,
    backend_url,
    selected_response_type,
    selected_model,
    set_tokens,
    temperature,
):
    if user_input:
        # add user input to session state
        st.session_state.responses.append({'user': user_input, 'bot': None})

        # prepare empty container to update the bot's response in real time
        response_container = st.empty()

        # Send the user input to backend API
        response = requests.post(
            backend_url,
            json={
                "message": user_input,
                "model": selected_model,
                "temperature": temperature,
                "max_tokens": set_tokens
            },
            stream=True,
        )
        print("response",response)

        if response.status_code == 200:
            bot_response = ""
            if selected_response_type == chatbot.output_type[0]:
                # stream response from backend
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    bot_response += chunk
                    # update response container with the latest bot response
                    response_container.markdown(
                        f"""
                        <div style="background-color:#262730; padding:10px; border-radius: 5px;">
                            <p style="font-family: Arial, sans-serif; font-color: #2f2f2f">{bot_response.strip()}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # # update the latest bot response in session state
                    # st.session_state.responses[-1]['bot'] = bot_response.strip()

            else:
                # collect the batch response
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    bot_response += chunk
                
                # display bot's response with adaptable height
                st.markdown(f"""
                    <div style="background-color:#f0f0f0; padding:10px; border-radius:5px;">
                        <p style="font-family:Arial, sans-serif;">{bot_response.strip()}</p>
                    </div>""", 
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
        st.session_state.current_input = ""

# main layout
def main():
    # display chat history first
    # display_chat_history()

    # collect user input below the chat history
    with st.form(key="input_form", clear_on_submit=True):
        # select model and training parameter
        selected_model = st.selectbox("Select your preferred model: ", chatbot.models)
        selected_response_type = st.selectbox("Select your preferred output type", chatbot.output_type)
        temperature = st.number_input(
            "Enter the parameter for model temperature (Number must be a float between 0 and 2)", 
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            format="%.1f"
        )
        set_tokens = st.selectbox("Please select length of output", chatbot.token_class.keys())
        user_input = st.text_input("You:", "")

        # submit button to send the input
        submit_button = st.form_submit_button(label="Send")

        # define the URL of the backend API
        if selected_response_type == chatbot.output_type[0]:
            backend_url = "http://127.0.0.1:5000/chat_stream"
        else:
            backend_url = "http://127.0.0.1:5000/chat_batch"
        
        if submit_button and user_input:
            print("HERE", user_input,
                backend_url,
                selected_response_type,
                selected_model,
                set_tokens,
                temperature,)
            handle_message(
                user_input=user_input,
                backend_url=backend_url,
                selected_response_type=selected_response_type,
                selected_model=selected_model,
                set_tokens=set_tokens,
                temperature=temperature,
            )

    
            
# # input text box for user input
# if 'current_input' not in st.session_state:
#     st.session_state.current_input = ""
# user_input = st.text_input("You:", st.session_state.current_input)

# if st.button("Send"):
#     handle_message(user_input)

if __name__ =="__main__":
    main()