# Theodore
 
🤖 Theodore – AI Hiring Assistant Chatbot

Theodore is a sleek, professional, and intelligent AI-powered interview assistant. Designed for streamlined, structured candidate evaluations, Theodore gathers applicant information step-by-step and tailors technical questions based on experience and skillset. Powered by locally hosted open-source LLMs (e.g., LLaMA2 or DeepSeek), Theodore provides a secure, customizable, and conversational interview experience in a minimalist dark-themed Streamlit UI.

## INSTALLATION

To run it locally, first, clone the repository.
Install dependencies
pip install -r requirements.txt

Run Ollama and pull your preferred model
ollama run <model> 
Note: I've used mistral-small3.1 but I've also tested it with llama2 (llama2:13b to be more particular)

Start the Streamlit app using streamlit run main.py

Theodore will greet you and start the interview.
Answer one question at a time.
Your answers are saved in a local SQLite database (interviews.db).
If you wish to restart the interview, click the 🔁 button.
If you wish to exit the interview, just tell Theodore that you want to! 

Theodore is smart and uses sentiment analysis, he would acknowledge if you are happy and would also offer to reschedule the interview at a later time if you are frustrated with the experience.

## Technical Details

Frontend: Streamlit (dark-themed chat UI)
Backend: Python, SQLite for local data storage
LLM: Ollama running mistral-small3.1
NLP: TextBlob for sentiment analysis
LangChain: Prompt handling and response streaming

## Architecture Overview

Modular code structure with main.py managing the app flow.
LLM calls routed through a reusable LangChain chain using a dynamic system prompt.
SQLite persists interview data after form completion.
Sentiment analysis provides empathetic feedback.
Step tracking ensures controlled, sequential interviews before technical questioning.

## PROMPT

Theodore's prompt design is thoughtfully structured to ensure a smooth, professional, and efficient interaction. The prompt consists of three core components: a system message that establishes Theodore’s formal, encouraging tone and behavioral guidelines; a chat history context that preserves the full conversation for the LLM to process in context; and a current_field tracker that determines what question should be asked next.

## CHALLANGES 

During development, maintaining the structured, step-by-step interview flow presented a key challenge. To address this, a step_index was introduced to track progress and enforce a strict one-question-at-a-time sequence. This ensured Theodore wouldn’t jump ahead or repeat steps unnecessarily.

Another major hurdle was choosing and running the language model itself. Many modern APIs require cloud hosting or subscription plans, which are often impractical for local development. This issue was resolved by integrating Ollama, allowing LLaMA2 and DeepSeek to run locally, thereby reducing dependency on third-party services.

Input validation also proved important. Candidates might accidentally provide incomplete or malformed email addresses or phone numbers, and we wanted to maintain a high standard of data accuracy. To handle this, custom regular expression checks were implemented for both fields, allowing Theodore to gracefully prompt for corrections when needed.

Emotional awareness was another advanced feature we wanted Theodore to have. Some candidates may feel nervous or discouraged during interviews. To detect such cases, TextBlob was integrated to analyze sentiment polarity. When negative sentiment is detected, Theodore responds empathetically, suggesting a pause or offering encouragement, making the interaction feel more human and supportive.

Lastly, we had to consider the possibility of language model hallucinations—instances where the LLM might fabricate facts, ask multiple questions at once, or stray from the defined behavior. To mitigate this, prompts were engineered with very strict formatting and instructions, clearly specifying that Theodore must ask only one question at a time and must not make assumptions. Additionally, context provided to the LLM is dynamically constructed from the actual conversation history, helping the model stay grounded and aligned with what the user has already said.


