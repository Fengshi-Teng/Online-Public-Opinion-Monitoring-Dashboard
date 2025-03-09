import praw
import os
import json
import requests
from bs4 import BeautifulSoup
from utils.analysis import get_subreddit
# from .analysis import summarize_post

from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_POSTS = 10
MAX_WORKERS = 8
SUB_COMMENTS_LIMIT = 3
COMMENT_SCORE_LIMIT = 100
AI_SUBREDDIT = False

reddit = praw.Reddit(
    client_id=os.environ.get("Reddit_Client_Id"),
    client_secret=os.environ.get("Reddit_Client_Secret"),
    user_agent="Emotion_Analysis",
)


def get_reddit_posts(subreddit="all", keyword=None, limit=5):
    '''
    TODO:
    '''
    subreddit_obj = reddit.subreddit(subreddit)
    
    if keyword:
        posts = subreddit_obj.search(keyword, limit=limit)
    else:
        posts = subreddit_obj.hot(limit=limit)
    results = []
    
    for post in posts:
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


def get_datas(post):
    '''
    TODO:
    '''
    post_url = post["post_url"]
    data = [post_url]
    if post.get("text_content"):
        data.append(((post["text_content"], post["score"])))
    submission = reddit.submission(url=post_url)
    submission.comments.replace_more(limit=SUB_COMMENTS_LIMIT)
    for comment in submission.comments:
        if comment.body == '[deleted]':
            continue
        if comment.score > COMMENT_SCORE_LIMIT:
            data.append((comment.body, comment.score))
    return data


def get_comments_parallel(keyword, max_workers=MAX_WORKERS) -> dict:
    '''
    TODO:
    '''
    subreddit = get_subreddit(keyword) if AI_SUBREDDIT else "all"
    posts = get_reddit_posts(subreddit=subreddit, keyword=keyword, limit=MAX_POSTS)
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_text = {executor.submit(get_datas, post): post for post in posts}
        for future in as_completed(future_to_text):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Error processing post: {future_to_text[future]['title']}, Error: {e}")
    return posts, results

# print(get_comments_parallel("tiktok")[1])