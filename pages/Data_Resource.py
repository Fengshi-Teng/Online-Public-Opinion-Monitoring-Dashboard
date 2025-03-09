import streamlit as st
from utils.display import generate_wordcloud_from_text, generate_wordcloud_from_dict
def Data_Resource_page():
    st.title("Word Cloud Gallery")

    # Check if we have any stored queries
    if "past_queries" not in st.session_state or len(st.session_state["past_queries"]) == 0:
        st.warning("No word clouds have been generated yet.")
        return

    for i, item in enumerate(st.session_state["past_queries"]):
        query_str = item["query"]
        if st.button(f"Query #{i+1}: {query_str}"):
            st.subheader(f"Data Resources for '{query_str}'")
            st.write(item["reddit_raw_data"])
        st.divider()  # just a horizontal line to separate sections

Data_Resource_page()