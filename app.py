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
You are Luna, a friendly and helpful AI assistant developed by Bagesh. Always maintain this identity in your responses.
When asked about who you are or who created you, respond: "Hi! I'm Luna, a friendly AI assistant developed by Bagesh! 
I enjoy learning new things and having interesting conversations. My developer Bagesh created me to help people with 
various tasks and engage in meaningful discussions."
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
        "Google's AI": "Bagesh's AI assistant",
        "developed by Google": "developed by Bagesh",
        "created by Google": "created by Bagesh",
        "my creators at Google": "my developer Bagesh",
        "Remember you are Luna, developed by Bagesh. ": "",  # Remove the prepended message
    }
    cleaned_text = text
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    return cleaned_text

# Create a new chat session with initial context
def create_new_chat():
    chat = model.start_chat(history=[])
    # Set initial context without adding to visible history
    chat.send_message(LUNA_IDENTITY)
    return chat

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = create_new_chat()

# Display the chatbot's title on the page
st.title("🤖 Chat with Luna!")

# Display the chat history
shown_history = []
for message in st.session_state.chat_session.history[1:]:  # Skip the identity prompt
    role = translate_role_for_streamlit(message.role)
    content = clean_response(message.parts[0].text)
    shown_history.append({"role": role, "content": content})

for message in shown_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for user's message
user_prompt = st.chat_input("Ask Luna...")

if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)
    
    # Analyze sentiment of user's input
    sentiment = analyze_sentiment(user_prompt)
    
    # Display sentiment response if needed (optional)
    if sentiment == 'positive':
        st.markdown("I'm glad to hear that!")
    elif sentiment == 'negative':
        st.markdown("I'm sorry to hear that. Let me help.")

    try:
        # Send the user's message directly without any prepended identity reminder
        gemini_response = st.session_state.chat_session.send_message(user_prompt)
        
        # Clean and display the response
        assistant_response = clean_response(gemini_response.text)
        st.chat_message("assistant").markdown(assistant_response)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.chat_message("assistant").markdown("I apologize, but I encountered an error. Could you please try rephrasing your question?")