import streamlit as st
import requests
import json

API_URL = "http://localhost:11434/api/chat"
MODEL = "chat_bot_gemma"

st.set_page_config(
    page_title="ChefMate - Chat Bot",
    page_icon=":shallow_pan_of_food:",  # This uses an emoji as the favicon. Replace with an image path if available.
    layout="centered",
    initial_sidebar_state="auto"
)

col1, col2 = st.columns([9, 1])
with col1:
    st.title("ChefMate - Chat Bot")
    st.markdown("""
        **Welcome to ChefMate!** 👨‍🍳
        
        ChefMate is your friendly culinary assistant here to help you with:
        - Finding recipes based on the ingredients you have
        - Suggesting meal plans tailored to your dietary preferences and calorie needs
        - Providing cooking tips and advice
        
        Just tell ChefMate what you need help with, and let’s get cooking!
    """)
with col2:
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)  # Add margin
    if st.button("Clear"):
        st.session_state.messages = []
        st.experimental_rerun()

# Initialize chat history if not already
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize input key if not already
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# Initialize loading state if not already
if "loading" not in st.session_state:
    st.session_state.loading = False

def send_and_display_streamed_response(chat_history):
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": MODEL,
        "messages": chat_history,
        "stream": True
    }
    response_started = False
    with requests.post(API_URL, headers=headers, json=data, stream=True) as response:
        if response.status_code == 200:
            placeholder = st.empty()
            temp_message = ""
            for line in response.iter_lines():
                if line:
                    if not response_started:
                        st.session_state.loading = False
                        response_started = True
                    json_data = json.loads(line.decode('utf-8'))
                    if 'message' in json_data:
                        # Display assistant message in chat message container
                        with placeholder.container():
                            st.chat_message("assistant")  # Specifying role
                            temp_message += json_data['message']['content']
                            st.write(temp_message)
                        if json_data.get('done', False):
                            break
            st.session_state.messages.append({"role": "assistant", "content": temp_message})
        else:
            st.session_state.loading = False
            st.error(f"Failed to connect: {response.status_code}")
            response.close()

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Custom CSS for small, grayed-out button text
st.markdown("""
    <style>
        .small-gray-button {
            font-size: 12px;
            color: gray;
            background-color: #f0f0f0;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
        }
        .small-gray-button:hover {
            color: black;
            background-color: #e0e0e0;
        }
    </style>
""", unsafe_allow_html=True)

# JavaScript for handling button clicks
st.markdown("""
    <script>
        function sendPrompt(prompt) {
            const input = window.parent.document.querySelector('input[data-testid="stChatInput"]');
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(input, prompt);
            const ev2 = new Event('input', { bubbles: true });
            input.dispatchEvent(ev2);
        }
    </script>
""", unsafe_allow_html=True)

# Suggested prompts
st.markdown("#### Suggested Prompts:")
st.markdown("""
    <button class="small-gray-button" onclick="sendPrompt('I want a recipe for dinner.')">I want a recipe for dinner.</button>
    <button class="small-gray-button" onclick="sendPrompt('I\'m looking for a meal plan.')">I'm looking for a meal plan.</button>
    <button class="small-gray-button" onclick="sendPrompt('Can you give me some cooking tips?')">Can you give me some cooking tips?</button>
""", unsafe_allow_html=True)

# Handle dynamic key for user input to reset the input field
input_key = f"user_input_{st.session_state.input_key}"

if st.session_state.loading:
    st.text_input("message ChefMate", key=input_key, disabled=True)
else:
    user_input = st.chat_input("message ChefMate", key=input_key)

if user_input:
    # Display user message in chat message container and add to history
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Set loading state
    st.session_state.loading = True

    with st.spinner("Processing..."):
        # Send updated chat history to the API and handle streamed responses
        send_and_display_streamed_response(st.session_state.messages)

    # Increment the key counter to reset the chat input
    st.session_state.input_key += 1

    # Clear the input field
    st.experimental_rerun()
