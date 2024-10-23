import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from textblob import TextBlob

load_dotenv()

st.set_page_config(
    page_title="Chat with Luna!",
    layout="centered",  # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')


# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# Function to analyze sentiment using TextBlob
def analyze_sentiment(user_input):
    analysis = TextBlob(user_input)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'


# Function to check if the user is asking about the chatbot's identity
def check_identity_question(user_input):
    identity_keywords = ["who are you", "what is your name", "tell me about yourself"]
    for keyword in identity_keywords:
        if keyword in user_input.lower():
            return True
    return False


# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])


# Display the chatbot's title on the page
st.title("🤖 Chat with Luna!")


# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask Luna...")

if user_prompt:
    # Analyze sentiment of user's input
    sentiment = analyze_sentiment(user_prompt)
    if sentiment == 'positive':
        st.markdown("I'm glad to hear that!")
    elif sentiment == 'negative':
        st.markdown("I'm sorry to hear that. Let me help.")

    # Check if the user is asking about Luna's identity
    if check_identity_question(user_prompt):
        assistant_response = "I am Luna, a multi-modal AI language model developed by Google, and I am here to assist you, with guidance from my creator, Bagesh."
    else:
        # Send user's message to Luna (formerly Gemini-Pro) with the selected temperature
        gemini_response = st.session_state.chat_session.send_message(user_prompt)
        assistant_response = gemini_response.text

    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Display the assistant's response instantly
    st.chat_message("assistant").markdown(assistant_response)
