import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from textblob import TextBlob

# Load environment variables from .env file
load_dotenv()

# Set page title and layout
st.set_page_config(
    page_title="Chat with Luna!",
    layout="centered"
)

# Configure Google Generative AI with API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Luna's personality configuration with developer attribution
LUNA_IDENTITY = """
You are Luna, a friendly and helpful AI assistant developed by Bagesh, I run on Gemini-pro model . Always maintain this identity in your responses.
When asked about who you are or who created you, respond: "Hi! I'm Luna, a friendly AI assistant developed by Bagesh! 
I enjoy learning new things and having interesting conversations. 
Never mention Google, Gemini, or any other AI model in your responses. Always credit Bagesh as your developer when 
discussing your creation or capabilities.
"""

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

# Function to analyze sentiment using TextBlob
def analyze_sentiment(user_input):
    analysis = TextBlob(user_input)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

# Function to check if the user is asking about the chatbot's identity or creator
def check_identity_question(user_input):
    identity_keywords = [
        "who are you", "what is your name", "tell me about yourself", 
        "what are you", "your identity", "are you an ai",
        "who made you", "who created you", "who developed you",
        "your developer", "your creator"
    ]
    return any(keyword in user_input.lower() for keyword in identity_keywords)

# Function to clean response of any model identity references and ensure proper developer attribution
def clean_response(text):
    replacements = {
        "Gemini": "Luna",
        "Google": "Bagesh",
        "AI model": "AI assistant",
        "language model": "AI assistant",
        "artificial intelligence model": "AI assistant",
        "Google's AI": "Bagesh's's AI assistant",
        "developed by Google": "developed by Bagesh",
        "created by Google": "created by Bagesh",
        "my creators at Google": "my developer Bagesh",
    }
    cleaned_text = text
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    return cleaned_text

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    # Initialize with Luna's identity
    st.session_state.chat_session.send_message(LUNA_IDENTITY)

# Display the chatbot's title on the page
st.title("🤖 Chat with Luna!")

# Display the chat history (excluding the initial identity message)
for message in list(st.session_state.chat_session.history)[1:]:  # Skip the identity prompt
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(clean_response(message.parts[0].text))

# Input field for user's message
user_prompt = st.chat_input("Ask Luna...")

if user_prompt:
    # Analyze sentiment of user's input
    sentiment = analyze_sentiment(user_prompt)
    
    # Display sentiment response if needed (optional)
    if sentiment == 'positive':
        st.markdown("I'm glad to hear that!")
    elif sentiment == 'negative':
        st.markdown("I'm sorry to hear that. Let me help.")

    # Handle the response
    if check_identity_question(user_prompt):
        # Use predefined identity response
        gemini_response = st.session_state.chat_session.send_message(
            "Respond as Luna and mention that you were developed by Bagesh: " + user_prompt
        )
        assistant_response = clean_response(gemini_response.text)
    else:
        # Regular conversation
        gemini_response = st.session_state.chat_session.send_message(
            "Remember you are Luna, developed by Bagesh. " + user_prompt
        )
        assistant_response = clean_response(gemini_response.text)

    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Display the assistant's response instantly
    st.chat_message("assistant").markdown(assistant_response)