# Theodore — AI-Powered Hiring Assistant 🤖

Theodore is a conversational AI hiring assistant built with **Streamlit**, **SQLite**, and a **locally hosted LLM (Ollama)**.  
It conducts structured interviews, collects candidate information step by step, and asks technical questions tailored to the candidate’s role and tech stack.
This project was built as a time-boxed engineering exercise, with an emphasis on correctness, state management, and reliability over polish.


## ✨ Features

- Conversational, chat-based interview flow
- Step-by-step profile collection (name, contact, role, experience, tech stack)
- Automatically generated technical questions
- Technical questions asked **one by one**
- All answers (profile + technical) stored in SQLite
- Clean session-based state handling
- Fully local inference (no external API calls)
- “🧠 Theodore is thinking…” spinner for better UX


## 🧠 Architecture Overview

- **Frontend**: Streamlit
- **LLM**: Local model via Ollama (e.g. `mistral-small`)
- **Database**: SQLite
- **State Management**: Streamlit `session_state`
- **Interview Flow**: Explicit phase-based state machine (`profile → technical → done`)


## ▶️ Running Locally

### Prerequisites
- Python 3.9+
- Ollama installed and running
- A local model pulled (e.g. `ollama pull mistral-small`)


