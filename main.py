import streamlit as st
import sqlite3
import re
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DB_PATH = "interviews.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
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
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS technical_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER,
        question TEXT,
        answer TEXT,
        question_order INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

def validate_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_phone(phone):
    return bool(re.match(r"^\d{10}$", phone))


st.set_page_config(
    page_title="Theodore – AI Interviewer",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Theodore — AI Hiring Assistant")


profile_fields = [
    ("name", "your full name"),
    ("phone_number", "your 10-digit phone number"),
    ("email_address", "your email address"),
    ("location", "your current location"),
    ("role", "the role you are applying for"),
    ("experience_years", "your years of experience"),
    ("tech_stack", "your main programming expertise"),
]


if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I’m Theodore. May I have your full name, please?"
    }]

if "phase" not in st.session_state:
    st.session_state.phase = "profile"

if "profile_step" not in st.session_state:
    st.session_state.profile_step = 0

if "tech_step" not in st.session_state:
    st.session_state.tech_step = 0

if "profile_answers" not in st.session_state:
    st.session_state.profile_answers = {}

if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []

if "interview_id" not in st.session_state:
    st.session_state.interview_id = None


if st.button("🔁 Restart Interview"):
    st.session_state.clear()
    st.rerun()


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


llm = Ollama(model="mistral-small3.2")
parser = StrOutputParser()

tech_q_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Generate exactly 3 basic technical interview questions
for a candidate applying for the role of {role}
with experience in {tech_stack}.
Return ONLY the questions, each on a new line.
""")
])

tech_q_chain = tech_q_prompt | llm | parser

ask_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are Theodore, a professional interviewer.
Acknowledge briefly, then ask ONLY this question:
{question}
"""),
    ("user", "{history}")
])

ask_chain = ask_prompt | llm | parser

if user_input := st.chat_input("Your response..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)


    if st.session_state.phase == "profile":
        key, label = profile_fields[st.session_state.profile_step]

        if key == "email_address" and not validate_email(user_input):
            st.error("Invalid email address.")
            st.stop()

        if key == "phone_number" and not validate_phone(user_input):
            st.error("Invalid phone number.")
            st.stop()

        st.session_state.profile_answers[key] = user_input
        st.session_state.profile_step += 1

        if st.session_state.profile_step == len(profile_fields):
            conn = get_conn()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO interview_data (
                    name, phone_number, email_address,
                    location, role, experience_years, tech_stack
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                st.session_state.profile_answers["name"],
                st.session_state.profile_answers["phone_number"],
                st.session_state.profile_answers["email_address"],
                st.session_state.profile_answers["location"],
                st.session_state.profile_answers["role"],
                int(st.session_state.profile_answers["experience_years"]),
                st.session_state.profile_answers["tech_stack"]
            ))

            conn.commit()
            st.session_state.interview_id = cur.lastrowid
            conn.close()

            raw = tech_q_chain.invoke({
                "role": st.session_state.profile_answers["role"],
                "tech_stack": st.session_state.profile_answers["tech_stack"]
            })

            st.session_state.tech_questions = [
                q.strip() for q in raw.split("\n") if q.strip()
            ]

            st.session_state.phase = "technical"

            st.session_state.messages.append({
                "role": "assistant",
                "content": st.session_state.tech_questions[0]
            })
            st.rerun()

        next_question = profile_fields[st.session_state.profile_step][1]


    elif st.session_state.phase == "technical":
        question = st.session_state.tech_questions[st.session_state.tech_step]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO technical_responses (
                interview_id, question, answer, question_order
            ) VALUES (?, ?, ?, ?)
        """, (
            st.session_state.interview_id,
            question,
            user_input,
            st.session_state.tech_step + 1
        ))

        conn.commit()
        conn.close()

        st.session_state.tech_step += 1

        if st.session_state.tech_step >= len(st.session_state.tech_questions):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Thank you. This concludes the interview."
            })
            st.session_state.phase = "done"
            st.rerun()

        next_question = st.session_state.tech_questions[st.session_state.tech_step]

    else:
        st.stop()

    history = "\n".join(m["content"] for m in st.session_state.messages)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 Theodore is thinking..."):
            response = ask_chain.invoke({
                "history": history,
                "question": next_question
            })
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
