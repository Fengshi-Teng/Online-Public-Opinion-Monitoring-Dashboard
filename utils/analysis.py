"""
analysis.py
===========
Fengshi Teng, Mar8 2025

This module provides functions and classes for data analysis, including data
cleaning, statistical computations, and visualization.

Key functionalities:
    - Data preprocessing and cleaning
    - Statistical analysis and computations
    - Visualization of analysis results
"""

import openai
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import time
start_time = time.time()

MAX_WORKERS = 12
# OpenAI API Key
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#### Part1: AI assistant in data searching
def input_summarize(input) -> str:
    """
    Extracts the most essential and minimal keywords from a given input text.

    The function removes unnecessary words and retains only the core nouns and 
    key phrases relevant to the topic.

    Parameters:
        input (str): The text input from which keywords should be extracted.

    Returns:
        str: A minimal set of keywords separated by spaces.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    '''
                    You are an expert at extracting concise and relevant search keywords.  
                    Your task is to extract **only the most essential and minimal keywords** from the given input.  
                    The keywords should be as short as possible while preserving the main topic.  

                    For example:
                    - **User Input:** "How is the most new iPhone?"  
                    **Response:** "iPhone"  
                    - **User Input:** "Best gaming laptops under $1000?"  
                    **Response:** "gaming laptops $1000"  
                    - **User Input:** "What are the effects of climate change on polar bears?"  
                    **Response:** "climate change polar bears"

                    **Rules:**  
                    1. Do **not** include unnecessary words (e.g., "how," "is," "the," "most").  
                    2. Focus only on **nouns, key phrases, or numbers** relevant to the query.  
                    3. **Do not explain.** Respond with only the essential keywords, separated by spaces. 
                    '''
                )
            },
            {
                "role": "user",
                "content": f"Extract minimal and essential keywords from: '{input}'"
            }
        ]
    )
    try:
        return response.choices[0].message.content.strip()
    except Exception:
        return


def get_subreddit(keywords) -> str:
    """
    Determines the most suitable subreddit for a given keyword or phrase.

    Parameters:
        keywords (str): A keyword or short phrase representing the topic.

    Returns:
        str: The name of the most relevant subreddit (without 'r/').

    Example:
        >>> get_subreddit("iPhone")
        "technology"
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant who is an expert in Reddit subreddits. "
                    "Your job is to decide which subreddit is the most suitable for a given keyword or phrase. "
                    "You must only return the subreddit name (just one word, without r/). "
                    "For example, if the keyword is 'iPhone', you should reply 'technology'. "
                    "No explanations, no extra words—just the subreddit name."
                )
            },
            {
                "role": "user",
                "content": f"Which subreddit is most suitable for the topic '{keywords}'? Reply only with the subreddit name."
            }
        ]
    )
    try:
        return response.choices[0].message.content.strip()
    except Exception:
        return


def summarize_post(post_url) -> str:
    """
    Summarizes the main topics, opinions, and emotions discussed in a Reddit post.
    Parameters:
        post_url (str): The URL of the Reddit post to be summarized.
    Returns:
        str: A summary of the main themes and opinions in the post (less than 100 words).
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant who is an expert in Reddit subreddits. "
                    "Your job is to summarize the post, including the overal topics, opinions and emotions."
                    "Your result should be less than 100 words."
                )
            },
            {
                "role": "user",
                "content": f"""
                Given the post '{post_url}'.
                Please analyze it and provide: the main topics being discussed.
                """
            }
        ]
    )
    try:
        return response.choices[0].message.content.strip()
    except Exception:
        return


#### Part2: AI analyist in people opinions and emotion
def analyze_sentiment(topic, text_and_score) -> dict:
    """
    Analyzes the sentiment of a given text and categorizes emotions with scores.
    Parameters:
        topic (str): The topic related to the analyzed text.
        text_and_score (tuple[str, int]): A tuple containing:
            - text (str): The text to analyze.
            - score (int): The weight or importance of the text.
    Returns:
        dict: A dictionary with emotion scores (joy, sadness, anger, fear, surprise, disgust)
              and key words that contributed to each emotion.
    """
    text = text_and_score[0]
    socre = text_and_score[1]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI that analyzes emotions in text."},
            {"role": "user",
             "content":f'''
              You're given a topic/summarize of the comments that you're going to analyse.
              Score each one of ollowing emotion types for the text:
             """joy, sadness, anger, fear, surprise, disgust.""" (total socre would be 100)
             Please attach each motion with a list of key words manifesting the emotion.
             Please just reply in the json format:
             """
                "joy": 5,
                "sadness": 45,
                "anger": 20,
                "fear": 10,
                "surprise": 20,
                "disgust": 0,
                "key words": ["word1", "word2"]
             """
             Topic:{topic}
             Text: {text}
            ''' }
        ]
    )
    try:
        res_json = response.choices[0].message.content.strip()[7:-3]
        emotion_scores = json.loads(res_json)
        for emo in emotion_scores.keys():
            if emo == "key words":
                continue
            emotion_scores[emo] *= socre
        # print(emotion_scores)
        return emotion_scores
    except Exception:
        return


def analyze_parallel(topic, texts, max_workers=MAX_WORKERS) -> dict:
    """
    Runs sentiment analysis in parallel on a list of texts.
    Parameters:
        topic (str): The topic related to the texts.
        texts (list[tuple[str, int]]): A list of (text, score) tuples.
        max_workers (int, optional): The number of threads to use for parallel
            execution. Defaults to 12.
    Returns:
        tuple[dict, dict]: 
            - A dictionary containing cumulative emotion scores.
            - A dictionary containing word frequencies from the analyzed texts.
    """
    emotion_score = {
        "joy": 0,
        "sadness": 0,
        "anger": 0,
        "fear": 0,
        "surprise": 0,
        "disgust": 0
    }
    word_cloud = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_text = {executor.submit(analyze_sentiment, topic, text): text for text in texts}
        for future in as_completed(future_to_text):
            emotions = future.result()
            emotion_score["joy"] += int(emotions["joy"])
            emotion_score["sadness"] += int(emotions["sadness"])
            emotion_score["anger"] += int(emotions["anger"])
            emotion_score["fear"] += int(emotions["fear"])
            emotion_score["surprise"] += int(emotions["surprise"])
            emotion_score["disgust"] += int(emotions["disgust"])
            for key_word in emotions["key words"]:
                word_cloud[key_word] = 1 if key_word not in word_cloud else word_cloud[key_word]+1
    return emotion_score, word_cloud


def summarize_sentiment(texts:list[str], summarize_detailed) -> str:
    """
    Generates a structured summary of the overall sentiment in a collection of texts.
    Parameters:
        texts (list[str]): A list of texts containing various opinions and emotions.
        summarize_detailed (int): Level of summary detail (1-10). 
            - 1: Brief high-level summary.
            - 10: In-depth analysis with examples and structure.
    Returns:
        str: A summary of emotional trends, including dominant sentiments, themes, and examples.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI that summarize the texts in terms of emotion."},
            {"role": "user",
             "content": f'''
            You are given a list of texts containing various emotions and opinions. 
            Your task is to summarize the overall sentiment and emotional trends from these texts.

            - Your summary detail level is {summarize_detailed} out of 10.
            - **1**: Provide a brief, high-level summary without examples.
            - **10**: Provide a detailed analysis with structured paragraphs, specific examples, and trends.

            **Instructions:**
            1. Identify the dominant emotions across the texts.
            2. Highlight recurring themes and opinions.
            3. If summarize_detailed is 5 or higher, include representative examples.
            4. If summarize_detailed is 8 or higher, structure the response with headings and bullet points.

            **Text Data:**
            {texts}
            '''}
        ]
    )
    return response.choices[0].message.content.strip()


def analyze_data(post_list: list, summarize_detailed) -> list:
    """
    Performs a complete sentiment analysis pipeline on a set of Reddit posts.
    Parameters:
        post_list (list[list]): A list where each element represents a post:
            - The first element is the post URL (str).
            - The remaining elements are tuples (text, score).
        summarize_detailed (int): The level of detail for sentiment summarization (1-10).
    Returns:
        tuple[dict, dict, str]:
            - Emotion score distribution (joy, sadness, anger, fear, surprise, disgust).
            - Word cloud dictionary with keyword frequencies.
            - A structured sentiment summary of the analyzed texts.
    """
    emotion_score = {
        "joy": 0,
        "sadness": 0,
        "anger": 0,
        "fear": 0,
        "surprise": 0,
        "disgust": 0
    }
    word_cloud = {}
    for post in post_list:
        try:
            topic = summarize_post(post[0])
            result, key_words = analyze_parallel(topic, post[1:])
            emotion_score["joy"] += int(result["joy"])
            emotion_score["sadness"] += int(result["sadness"])
            emotion_score["anger"] += int(result["anger"])
            emotion_score["fear"] += int(result["fear"])
            emotion_score["surprise"] += int(result["surprise"])
            emotion_score["disgust"] += int(result["disgust"])
            for key_word, num in key_words.items():
                word_cloud[key_word] = num if key_word not in word_cloud else word_cloud[key_word]+num
        except Exception as e:
            print(e)
            continue
    return emotion_score, word_cloud, summarize_sentiment(post_list, summarize_detailed)
