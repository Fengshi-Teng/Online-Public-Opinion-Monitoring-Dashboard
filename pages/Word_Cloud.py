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
            st.image(generate_wordcloud_from_text(data), caption=f"Word Cloud for '{query_str}'", use_container_width=True)
            st.subheader(f"Word Cloud for '{query_str}' after Emotional Analysis")
            data = item["word_cloud"]
            st.image(generate_wordcloud_from_dict(data), caption=f"Word Cloud for '{query_str}'", use_container_width=True)

        st.divider()  # just a horizontal line to separate sections

wordcloud_page()