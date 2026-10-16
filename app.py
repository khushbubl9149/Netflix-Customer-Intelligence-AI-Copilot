
import sys
from pathlib import Path

import streamlit as st

# Add project root so the existing backend can be imported.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.copilot.question_router import generate_answer


st.set_page_config(
    page_title="Netflix Customer Intelligence AI Copilot",
    page_icon="🎬",
    layout="wide",
)

st.markdown("""
<style>
.main {
    background-color: #101014;
}
[data-testid="stAppViewContainer"] {
    background-color: #101014;
}
[data-testid="stSidebar"] {
    background-color: #19191f;
}
h1, h2, h3, p, label {
    color: #f5f5f5;
}
.hero {
    padding: 24px;
    border-radius: 14px;
    background: linear-gradient(120deg, #351018, #19191f);
    border: 1px solid #57232b;
    margin-bottom: 20px;
}
.hero p {
    color: #dddddf;
}
div[data-testid="stMetric"] {
    background: #1b1b22;
    padding: 18px;
    border: 1px solid #34343d;
    border-radius: 12px;
}
.stButton button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.title("🎬 Netflix Copilot")
    st.caption("Customer Intelligence Dashboard")
    st.divider()

    st.subheader("Quick questions")
    quick_questions = [
        "What is the overall churn rate?",
        "How many total customers are there?",
        "What is the churn risk for CUST002668?",
        "What retention actions do you recommend for CUST002668?",
        "Why is CUST002668 at high churn risk?",
    ]

    for question in quick_questions:
        if st.button(question, use_container_width=True):
            st.session_state.pending_question = question

    st.divider()
    st.caption("Powered by Python, SQL and Machine Learning")


st.markdown("""
<div class="hero">
    <h1>Netflix Customer Intelligence AI Copilot</h1>
    <p>
        Understand customer churn, explore customer risk, and get
        retention recommendations using your existing AI Copilot.
    </p>
</div>
""", unsafe_allow_html=True)


st.subheader("Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", "8,000")
col2.metric("Churned Customers", "1,991")
col3.metric("Active Customers", "6,009")
col4.metric("Overall Churn Rate", "24.89%")

st.caption(
    "KPI values reflect your last verified backend result. "
    "They are display values and do not automatically refresh."
)

st.divider()
st.subheader("Ask Your AI Copilot")
st.write(
    "Ask about churn statistics, customer risk, or retention actions."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def ask_copilot(question):
    question = question.strip()
    if not question:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            try:
                answer = generate_answer(question)
            except Exception as exc:
                answer = (
                    "I couldn't process this question. "
                    "Please check the database connection and "
                    "application terminal for details."
                )
                print(f"Copilot error: {exc}")

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })


if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")
    ask_copilot(question)

prompt = st.chat_input(
    "e.g. What is the overall churn rate?"
)

if prompt:
    ask_copilot(prompt)

st.divider()
st.caption("Netflix Customer Intelligence AI Copilot | Project Demo")
