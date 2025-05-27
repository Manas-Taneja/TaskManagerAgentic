# app.py
import streamlit as st
from ai_task_manager.task_manager import TaskManager
from ai_task_manager.llm_service import LLMService
from ai_task_manager.search_service import SearchService
from ai_task_manager.database import TaskDatabase

st.set_page_config(page_title="Agentic Task Manager", layout="wide")
st.title("🧠 Agentic AI Task Manager")

task_title = st.text_input("📝 Task Title")
task_desc = st.text_area("📌 Task Description")
priority = st.slider("🚦 Priority", 1, 5, 3)

if st.button("Add Task & Generate Insights"):
    db = TaskDatabase()
    searcher = SearchService()
    llm = LLMService()
    agent = TaskManager(db=db, search_service=searcher, llm_service=llm)

    task = agent.add_task(task_title, task_desc, priority)
    st.success(f"✅ Task #{task['id']} added.")

    with st.spinner("🔍 Searching for resources..."):
        agent.search_and_add_resources(task['id'])
    with st.spinner("🧠 Generating insights..."):
        agent.generate_and_add_insight(task['id'])

    task = agent.get_task(task['id'])

    if task.get("insights"):
        latest_insight = task["insights"][-1]["content"]
        st.markdown("### 🧠 Insight:")
        st.markdown(latest_insight)
    else:
        st.warning("⚠️ No insight found for this task.")

    # 👉 Show digest preview after insight is ready
    with st.expander("📬 Preview Daily Digest"):
        digest = agent.generate_daily_digest()
        st.markdown(digest)

    st.success("✨ Done!")



if st.button("📬 Generate Digest"):
    from ai_task_manager.email_service import EmailService
    agent = TaskManager()
    digest = agent.generate_daily_digest()
    st.markdown(digest)

    if st.button("📤 Email Digest"):
        emailer = EmailService()
        emailer.send_daily_digest(digest)
        st.success("Sent!")

