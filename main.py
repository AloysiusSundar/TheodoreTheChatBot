import streamlit as st
import sqlite3
import re
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from textblob import TextBlob

conn = sqlite3.connect('interviews.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone_number TEXT,
        email_address TEXT,
        location TEXT,
        role TEXT,
        experience_years INTEGER,
        tech_stack TEXT
    )
''')
conn.commit()

def detect_exit_keywords(user_input):
    exit_keywords = [
        "quit", "exit", "stop", "end interview", "cancel", 
        "leave", "not now", "pause", "maybe later"
    ]
    return any(keyword in user_input.lower() for keyword in exit_keywords)


# Validate email
def validate_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_phone(phone):
    return bool(re.match(r'^\d{10}$', phone))

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1.0 (negative) to 1.0 (positive)
    return polarity

# Page config
st.set_page_config(page_title="Theodore – AI Interviewer", page_icon="🤖", layout="centered")
st.title("🤖 AI-Powered Hiring Assistant")

# List of fields to collect in order
interview_fields = [
    "name",
    "phone number",
    "email address",
    "location",
    "role applying for",
    "years of experience",
    "tech stack / main programming expertise"   
]


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I’m Theodore, your AI interview assistant. Let’s begin — may I have your name, please?"}
    ]
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "step_index" not in st.session_state:
    st.session_state.step_index = 0

# Restart button
if st.button("🔁 Restart Interview"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I’m Theodore, your AI interview assistant. Let’s begin — may I have your name, please?"}
    ]
    st.session_state.answers = {}
    st.session_state.step_index = 0
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Define prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
You are Theodore, a professional, formal, and encouraging AI interviewer.

You are collecting candidate information step-by-step. At each step, do the following:
- Acknowledge the user's latest answer.
- Ask for exactly one item from the list, in order:
  1. Name
  2. Phone number
  3. Email address
  4. Location
  5. Role applying for
  6. Years of experience
  7. Tech stack / main programming expertise

After collecting all 7 fields, ask **only 3 very basic technical questions** tailored to the role and tech stack.

You must now ask for the following field: **{current_field}**
If {current_field} is 'technical questions', begin with the first technical question. 
Do not ask more than three technical questions in total.
Do not ask about anything else or ask multiple questions.
Do not assume or guess the user's info. Remain formal and concise but be warm and encouraging when you acknowledge.
"""),
    ("user", "{chat_history}")
])

# Setup LLM
llm = Ollama(model="mistral-small3.1")
output_parser = StrOutputParser()
chain = prompt_template | llm | output_parser

def save_interview_data(data):
    cursor.execute('''
        INSERT INTO interview_data (name, phone_number, email_address, location, role, tech_stack, experience_years)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('phone_number'),
        data.get('email_address'),
        data.get('location'),
        data.get('role'),
        data.get('experience_years'),
        data.get('tech_stack')
    ))
    conn.commit()

# Chat input
if user_input := st.chat_input("Your response..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    if detect_exit_keywords(user_input):
        st.session_state.messages.append({"role": "assistant", "content": "Understood. Ending the interview here. Thank you for your time!"})
        st.rerun()
        
    sentiment_score = analyze_sentiment(user_input)
    if sentiment_score < -0.5:
        st.warning("You seem upset. If you’d like to pause or restart the interview, feel free to let me know.")
    elif sentiment_score > 0.5:
        st.success("I'm glad you're feeling positive!")
    
    if st.session_state.step_index == 2:  # Email step (index 2 corresponds to email)
        if not validate_email(user_input):
            st.error("Invalid email address. Please enter a valid email.")
            st.session_state.step_index -= 1  # Stay on the email step
        else:
            st.session_state.answers["email address"] = user_input
            st.session_state.step_index += 1 
            
    if st.session_state.step_index == 1:  # Phone number step
        if not validate_phone(user_input):
            st.error("Invalid phone number. Please enter a valid 10-digit phone number.")
        else:
            st.session_state.answers["phone number"] = user_input

    # Save user's answer if within the expected steps
    # Save user's answer if within the expected steps
    if st.session_state.step_index < len(interview_fields):
        current_field = interview_fields[st.session_state.step_index]
        st.session_state.answers[current_field] = user_input
        st.session_state.step_index += 1


    # Determine next field or enter technical phase
    if st.session_state.step_index < len(interview_fields):
        current_field = interview_fields[st.session_state.step_index]
    else:
        current_field = "technical questions"

    # Rebuild full chat history
    full_history = "\n".join([
    msg["content"] for msg in st.session_state.messages
])

    # Invoke LLM
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Theodore is thinking..."):
            response = chain.invoke({
                "chat_history": full_history,
                "current_field": current_field
            })
            st.markdown(response)

    # Append assistant's message
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    if st.session_state.step_index == len(interview_fields):
        save_interview_data(st.session_state.answers)