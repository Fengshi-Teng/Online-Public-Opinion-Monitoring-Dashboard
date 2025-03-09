import streamlit as st
from utils.display import generate_wordcloud_from_text, generate_wordcloud_from_dict
def History_Summary_page():
    st.title("History Summaries")

    # Check if we have any stored queries
    if "past_queries" not in st.session_state or len(st.session_state["past_queries"]) == 0:
        st.warning("No word clouds have been generated yet.")
        return

    for i, item in enumerate(st.session_state["past_queries"]):
        query_str = item["query"]
        if st.button(f"Query #{i+1}: {query_str}"):
            if not "summarize" in item:
                st.write("No records.")
                continue
            st.subheader(f"Public Opinion Trend Summary for '{query_str}'")
            st.write(item["summarize"])
            st.write(item["rose_chart"])
        st.divider()  # just a horizontal line to separate sections

History_Summary_page()