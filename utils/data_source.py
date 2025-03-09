"""
Reddit Data Fetching and Comment Extraction
===========================================
Fengshi Teng, Mar8 2025

This module provides functionality for fetching posts and comments from Reddit 
based on keywords or subreddit searches. It supports parallel processing for 
efficient data retrieval.

Key functionalities:
    - Fetching Reddit posts based on keywords or subreddit filters.
    - Extracting high-quality comments with a minimum upvote threshold.
    - Performing parallelized data collection for efficiency.
"""


import praw
import os
import json
import requests
import time
from bs4 import BeautifulSoup
from utils.analysis import get_subreddit

from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_POSTS = 10
MAX_WORKERS = 12
SUB_COMMENTS_LIMIT = 3
COMMENT_SCORE_LIMIT = 100
AI_SUBREDDIT = False

reddit = praw.Reddit(
    client_id=os.environ.get("Reddit_Client_Id"),
    client_secret=os.environ.get("Reddit_Client_Secret"),
    user_agent="Emotion_Analysis",
)


def get_reddit_posts(subreddit="all", keyword=None, limit=5, days=90):
    '''
    Fetches recent Reddit posts from a specified subreddit, with optional keyword filtering.

    Parameters:
        subreddit (str, optional): The subreddit to search within. Defaults to "all".
        keyword (str, optional): A keyword to filter posts. If None, fetches the top hot posts.
        limit (int, optional): The number of posts to retrieve. Defaults to 5.
        days (int, optional): Time filter to exclude posts older than this many days. Defaults to 90.

    Returns:
        list[dict]: A list of dictionaries containing post details:
            - title (str): The post title.
            - score (int): The post's Reddit score (upvotes - downvotes).
            - num_comments (int): Number of comments on the post.
            - post_url (str): Direct URL to the Reddit post.
            - link_url (str): External link in the post (if any).
            - time (float): Post creation time (UTC timestamp).
            - text_content (str | None): Post text content (if available).
    '''
    subreddit_obj = reddit.subreddit(subreddit)
    
    if keyword:
        posts = subreddit_obj.search(keyword, sort="hot", limit=limit)
    else:
        posts = subreddit_obj.hot(limit=limit)

    time_threshold = time.time() - (days * 86400)
    results = []
    
    for post in posts:
        if post.created_utc <= time_threshold: 
            continue
        results.append({
            "title": post.title,
            "score": post.score,
            "num_comments": post.num_comments,
            "post_url": f"https://www.reddit.com{post.permalink}",
            "link_url": post.url,
            "time": post.created_utc,
            "text_content": post.selftext if post.selftext else None
        })

    return results


def get_datas(post, comment_depth, min_upvotes):
    '''
    Extracts text data from a Reddit post and its top comments.

    Parameters:
        post (dict): A dictionary containing post metadata (from `get_reddit_posts`).
        comment_depth (int): Maximum number of nested comment levels to retrieve.
        min_upvotes (int): Minimum upvotes required for a comment to be included.

    Returns:
        list: A list containing:
            - The post URL (str).
            - The post text content and score (tuple[str, int]), if available.
            - A list of (comment text, score) tuples for comments meeting the upvote threshold.
    '''
    post_url = post["post_url"]
    data = [post_url]
    if post.get("text_content"):
        data.append(((post["text_content"], post["score"])))
    submission = reddit.submission(url=post_url)
    submission.comments.replace_more(limit=comment_depth)
    for comment in submission.comments:
        if comment.body == '[deleted]':
            continue
        if comment.score > min_upvotes:
            data.append((comment.body, comment.score))
    return data


def get_comments_parallel(keyword, num_results, comment_depth, min_upvotes, use_ai_partitioning, max_workers=MAX_WORKERS) -> dict:
    '''
    Fetches Reddit posts and extracts high-quality comments in parallel.

    Parameters:
        keyword (str): The keyword for Reddit post search.
        num_results (int): Number of posts to retrieve.
        comment_depth (int): Number of nested comment levels to extract.
        min_upvotes (int): Minimum upvotes required for a comment to be included.
        use_ai_partitioning (bool): Whether to use AI-based subreddit selection.
        max_workers (int, optional): Number of parallel threads for fetching data. Defaults to MAX_WORKERS.

    Returns:
        tuple[list[dict], list[list]]:
            - A list of post metadata dictionaries.
            - A list of extracted post data (each containing post URL, text content, and selected comments).
    '''
    subreddit = get_subreddit(keyword) if use_ai_partitioning else "all"
    posts = get_reddit_posts(subreddit=subreddit, keyword=keyword, limit=num_results)
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_text = {executor.submit(get_datas, post, comment_depth, min_upvotes): post for post in posts}
        for future in as_completed(future_to_text):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Error processing post: {future_to_text[future]['title']}, Error: {e}")
    return posts, results
