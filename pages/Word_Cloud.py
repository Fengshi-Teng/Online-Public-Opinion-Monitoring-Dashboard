"""
Streamlit App - Word Cloud Gallery
==================================
Fengshi Teng, Mar 8 2025

This module defines the "Word Cloud Gallery" page for the Public Opinion Trend 
Analysis Tool, allowing users to visualize word frequency distributions from 
past sentiment analysis queries.

Key Features:
    - Displays word clouds generated from raw Reddit comments.
    - Shows word clouds after emotional analysis filtering.
    - Allows users to select past queries to view their corresponding word clouds.
    - Displays a warning if no word clouds have been generated.
"""
import streamlit as st
from utils.display import generate_wordcloud_from_text, generate_wordcloud_from_dict


def wordcloud_page():
    st.title("Word Cloud Gallery")
    # Check if we have any stored queries
    if "past_queries" not in st.session_state or len(st.session_state["past_queries"]) == 0:
        st.warning("No word clouds have been generated yet.")
        return

    for i, item in enumerate(st.session_state["past_queries"]):
        query_str = item["query"]
        if st.button(f"Query #{i+1}: {query_str}"):
            st.subheader(f"Word Cloud for '{query_str}' from Raw Text")
            data = "".join(["".join([comment[0] for comment in comment_list[1:]]) for comment_list in item["comments_data"]])
            st.image(generate_wordcloud_from_text(data), caption=f"Word Cloud for '{query_str}'", width = 1000)
            st.subheader(f"Word Cloud for '{query_str}' after Emotional Analysis")
            data = item["word_cloud"]
            st.image(generate_wordcloud_from_dict(data), caption=f"Word Cloud for '{query_str}'", width = 1000)

        st.divider()  # just a horizontal line to separate sections

wordcloud_page()