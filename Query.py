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
# Customize data range
num_results = st.slider("Number of posts to fetch", min_value=3, max_value=30, value=10, step=1)
comment_depth = st.slider("Comment depth (nested levels)", min_value=1, max_value=5, value=2, step=1)
min_upvotes = st.slider("Minimum upvotes required", min_value=50, max_value=200, value=100, step=10)
summarize_detailed = st.slider("Summarize details", min_value=1, max_value=10, value=2, step=1)
use_ai_partitioning = st.toggle("Enable AI-powered subreddit filtering")
estimated_time = (15 + num_results * 2) * (comment_depth ** 1.2) / (min_upvotes/50)**0.5
if use_ai_partitioning:
    estimated_time += 3  # AI filtering adds processing time
st.info(f"⏳ Estimated search time: ~{round(estimated_time, 1)} seconds")

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
            reddit_raw_data, comments_data = get_comments_parallel(keywords, num_results, comment_depth, min_upvotes, use_ai_partitioning)
            placeholder.success("Data retrieved successfully!")

            # Perform sentiment analysis
            with st.spinner(f"Performing sentiment analysis..."):
                emotion_score, word_cloud, summarize = analyze_data(comments_data, summarize_detailed)

            # Display the analysis results
            placeholder.empty()
            st.subheader("Analysis Results")
            st.write(summarize)
            rose_chart = display_rose_chart(emotion_score).gcf()
            st.pyplot(rose_chart)

            # store data
            if "past_queries" not in st.session_state:
                st.session_state["past_queries"] = []
            st.session_state["past_queries"].append({
                "query": user_input,
                "word_cloud": word_cloud,
                "reddit_raw_data": reddit_raw_data,
                "comments_data": comments_data,
                "summarize": summarize,
                "rose_chart": rose_chart
            })

            

        except Exception as e:
            st.error(f"Fail to analyse: {e}")
