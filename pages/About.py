import streamlit as st

# About Page Content
st.title("📌 About This App")

## Copyright Information
st.write("### 📜 Copyright")
st.write("This app is created and maintained by **Fengshi Teng**. All rights reserved.")

## Background Introduction
st.write("### 🎯 Background")
st.write("""
This app is designed as a **public opinion monitoring dashboard**, helping users quickly understand **public sentiment trends and hot topics**.  
Instead of manually browsing through large amounts of posts and comments, this tool **saves time** and provides **a structured summary of online discussions**.
""")

## Technology Stack
st.write("### 🔧 Technology Stack")
st.write("""
- **📊 Data Source:**  
  - Currently, the app collects **publicly available discussions from Reddit**.  
    *(As a demo, it's enough, but in the future, it can be expanded to wider sources.)*
  - Future updates may integrate **other public opinion data APIs**.

- **🧠 AI-powered Analysis:**  
  - Uses **OpenAI's GPT models** for **summarization, sentiment analysis, and topic extraction**.

- **🖥️ Presentation:**  
  - Built with **Streamlit**, providing an **interactive and user-friendly interface**.
""")

st.write("---")
st.info("🚀 More features will be added soon! Stay tuned for future updates.")