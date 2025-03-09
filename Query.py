import streamlit as st
from utils.ui import load_custom_css
from utils.analysis import input_summarize, analyze_data
from utils.data_source import get_comments_parallel
from utils.display import display_rose_chart
import matplotlib.pyplot as plt

st.set_page_config(page_title="Public Opinion Trend Analysis", layout="wide")
load_custom_css("utils/style.css")

st.title("Public Opinion Trend Analysis Tool")
st.subheader("(Reddit version)")

st.markdown(
    """
    <style>
    /* Your custom CSS here */
    </style>
    """,
    unsafe_allow_html=True
)

# Get user input
user_input = st.text_input("Enter the topic you want to analyze")
if st.button("Start Analysis"):
    placeholder = st.empty()
    if not user_input.strip():
        st.error("Please enter a valid keyword!")
    else:
        placeholder.info("Processing keywords...")

        # Process keywords
        keywords = input_summarize(user_input)
        st.write(f"Extracted keywords: {keywords}")

        # Fetch relevant posts and comments from Reddit
        placeholder.info("Fetching relevant comments from Reddit...")
        try:
            reddit_raw_data, comments_data = get_comments_parallel(keywords)
            placeholder.success("Data retrieved successfully!")

            # Perform sentiment analysis
            with st.spinner("Performing sentiment analysis, please wait ~30 seconds..."):
                emotion_score, word_cloud, summarize = analyze_data(comments_data)

            # store data
            if "past_queries" not in st.session_state:
                st.session_state["past_queries"] = []
            st.session_state["past_queries"].append({
                "query": user_input,
                "word_cloud": word_cloud,
                "reddit_raw_data": reddit_raw_data,
                "comments_data": comments_data
            })

            # Display the analysis results
            placeholder.empty()
            st.subheader("Analysis Results")
            st.write(summarize)
            st.pyplot(display_rose_chart(emotion_score).gcf())


        except Exception as e:
            st.error(f"Fail to analyse: {e}")
