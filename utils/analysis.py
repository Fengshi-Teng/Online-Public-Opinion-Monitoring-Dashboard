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
    '''
    TODO:
    '''
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
    '''
    TODO:
    '''
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
    '''
    TODO:
    '''
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


# posts = ['https://www.reddit.com/r/TikTokCringe/comments/1igeoz3/tiktoker_tries_to_show_love_to_homeless_person/', ('She just gave the tik toker a dose of her own medicine', 13336), ('“We’re trying to help you”… by waking her up and posting it on TikTok? \nGood one.', 5384), ('No telling how many times she has been woken up just to be annoyed or fucked with in some way. If they truly thought she needed help, there were other better ways to go about it.', 2475), ("I can't believe this went on for as long as it did after she licked her", 3970), ('You know what? Good for her. The homeless lady knew exactly what she was doing and played this perfectly.', 5316), ('That was pretty smart on the part of the homeless person. “Oh you can just come up and put hands on me? Try this!”', 1428), ('Hey touch rando people and be offended when they touch you back. Stay classy.', 750), ('“Why don’t you love yourself” was ice cold', 1103), ("people who do this bullshit don't see homeless people as people, but tools. It's poverty porn and I fucking hate it.", 170), ('Disturbs a homeless woman\n\nShe acts aggressively\n\nThe content creators:\n\n![gif](giphy|6nWhy3ulBL7GSCvKw6)', 1536), ('Homeless women are not dogs to befriend. A lot of times they’re hyper-vigilant because of how vulnerable they are, and SA and other violence against women happens all the time in homeless spaces. Walking up on her and trying to touch her was extremely insensitive and dangerous for everyone involved. Next time work with an established organization that knows more about their community than you do, and keep the cameras and social media clout chasing out of the equation. All they’re doing is making her mental state worse here.', 505), ('Please stop touching people without consent.', 571), ('I don\'t trust anyone to tell me the "truth on the streets" when they display such a lack of street smarts.\xa0 They\'re lucky this poor woman probably wasn\'t as crazy as she was acting, she could have just as easily been stabbed as she was licked.\xa0 A lack of respect on multiple levels.', 217), ("Wow not cool homeless person. You're supposed to lay there and be used as a tool.", 183), ('If you were trying to help her, why did it need to be filmed??? Ppl go through things and don’t want to be used for content! Isn’t it bad enough that she is homeless?? The Tik Toker got what she was looking for. She wasn’t being genuine. She was looking for clout.', 275), ('She hands out clothing and other items for houseless people in Portland in exchange for content/sharing their picture. I’ve seen her first hand approaching people in crisis to give them things so she can take videos or “portraits” of them to share on social media. She almost always is with Kevin Dahlgren who was convicted of theft, identity theft and official misconduct and was stealing from homeless services, even though he claims to “help” houseless people. People need to stop giving her any attention and they both need to crawl back into whatever hole they came out of.\n\nEdit: Source for Kevin https://www.oregonlive.com/crime/2025/01/kevin-dahlgren-prominent-critic-of-portland-homeless-services-admits-to-stealing-from-them.html', 335), ("# Oh, you don't like that either?\n\n![gif](giphy|J8FZIm9VoBU6Q)", 142), ('maybe just leave people alone, especially angry addicted homeless people you want to film for clout', 370)]
# topic = summarize_post(posts[0])
# print(analyze_parallel(topic, posts[1:]))
# # print(analyze_parallel(topic, posts[1:]))
# # print(analyze_data([posts]))
# test = [['https://www.reddit.com/r/TikTokCringe/comments/1abx82t/shout_out_to_all_the_invisible_cameramen_of_tiktok/', ("I've seen that shirtless guy that fucks you video a couple of times and it's always the most excruciatingly unconformable shit in this planet, makes my skin crawl.", 1847), ('Stupid sexy Flanders!', 318), ('The squeak toy sound effect for the lizard had me in FITS', 616), ('His videos give me giggle fits. Every damn time.', 579), ("I'm fucking dying, this is hilarious.", 245), ('Love his channel, dude is hilarious. I think the funniest thing is the invisible cameramen he employs to do his invisible cameraman bits. It’s cameramen all the way down.', 229)], ['https://www.reddit.com/r/TikTokCringe/comments/1igeoz3/tiktoker_tries_to_show_love_to_homeless_person/', ('She just gave the tik toker a dose of her own medicine', 13341), ('“We’re trying to help you”… by waking her up and posting it on TikTok? \nGood one.', 5385), ('No telling how many times she has been woken up just to be annoyed or fucked with in some way. If they truly thought she needed help, there were other better ways to go about it.', 2477), ("I can't believe this went on for as long as it did after she licked her", 3970), ('You know what? Good for her. The homeless lady knew exactly what she was doing and played this perfectly.', 5327), ('That was pretty smart on the part of the homeless person. “Oh you can just come up and put hands on me? Try this!”', 1427), ('Hey touch rando people and be offended when they touch you back. Stay classy.', 748), ('“Why don’t you love yourself” was ice cold', 1107), ("people who do this bullshit don't see homeless people as people, but tools. It's poverty porn and I fucking hate it.", 171), ('Disturbs a homeless woman\n\nShe acts aggressively\n\nThe content creators:\n\n![gif](giphy|6nWhy3ulBL7GSCvKw6)', 1540), ('Homeless women are not dogs to befriend. A lot of times they’re hyper-vigilant because of how vulnerable they are, and SA and other violence against women happens all the time in homeless spaces. Walking up on her and trying to touch her was extremely insensitive and dangerous for everyone involved. Next time work with an established organization that knows more about their community than you do, and keep the cameras and social media clout chasing out of the equation. All they’re doing is making her mental state worse here.', 496), ('Please stop touching people without consent.', 578), ('I don\'t trust anyone to tell me the "truth on the streets" when they display such a lack of street smarts.\xa0 They\'re lucky this poor woman probably wasn\'t as crazy as she was acting, she could have just as easily been stabbed as she was licked.\xa0 A lack of respect on multiple levels.', 221), ('This is awesome lmfao.\n\nShe scared the fuck out of those streamer dipshits', 104), ("Wow not cool homeless person. You're supposed to lay there and be used as a tool.", 186), ('If you were trying to help her, why did it need to be filmed??? Ppl go through things and don’t want to be used for content! Isn’t it bad enough that she is homeless?? The Tik Toker got what she was looking for. She wasn’t being genuine. She was looking for clout.', 275), ('She hands out clothing and other items for houseless people in Portland in exchange for content/sharing their picture. I’ve seen her first hand approaching people in crisis to give them things so she can take videos or “portraits” of them to share on social media. She almost always is with Kevin Dahlgren who was convicted of theft, identity theft and official misconduct and was stealing from homeless services, even though he claims to “help” houseless people. People need to stop giving her any attention and they both need to crawl back into whatever hole they came out of.\n\nEdit: Source for Kevin https://www.oregonlive.com/crime/2025/01/kevin-dahlgren-prominent-critic-of-portland-homeless-services-admits-to-stealing-from-them.html', 334), ("# Oh, you don't like that either?\n\n![gif](giphy|J8FZIm9VoBU6Q)", 142), ('maybe just leave people alone, especially angry addicted homeless people you want to film for clout', 366)]]
# print(analyze_data(test))

# end_time = time.time()
# print(end_time-start_time)