import praw
import os
import time
import logging
import random
import re
from groq import Groq
import tweepy

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reddit API authentication
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    user_agent="firescan_deepseek_bot"
)

# Target subreddit
subreddit = reddit.subreddit("wildfire")

# List of prompts for variety
prompts = [
    "Write a Reddit post about a recent wildfire, its impact, and how FireScan helps detect and mitigate wildfires using AI-powered drones. FireScan integrates multiple satellite data sources for early wildfire detection and prediction, providing real-time insights to firefighters.",
    "How can AI-powered systems like FireScan prevent wildfires before they get out of control? Write a discussion post about the role of AI in early wildfire detection, using real-time satellite data and predictive models.",
    "FireScan is an AI-driven wildfire detection and response system. It integrates multiple satellite sources, advanced sensing capabilities, and autonomous drone deployment to help firefighters combat wildfires effectively. Write a Reddit post discussing how this technology can transform wildfire management.",
    "A wildfire broke out in Australia and California. FireScan, an AI-driven wildfire detection platform, provided early warnings that helped firefighters deploy resources efficiently. Write a news-style Reddit post discussing how AI and drones improve wildfire response times.",
    "Wildfires are becoming more frequent and severe. FireScan acts as a community fire reporting tool, quickly alerting authorities as AI processes multiple data sources for early detection. Write a Reddit discussion post about the importance of rapid wildfire reporting."
]

# Groq (DeepSeek) API client setup
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key)

# Twitter API client setup using Tweepy
twitter_api_key = os.getenv("TWITTER_API_KEY")
twitter_api_key_secret = os.getenv("TWITTER_API_KEY_SECRET")
twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

auth = tweepy.OAuth1UserHandler(twitter_api_key, twitter_api_key_secret,
                                twitter_access_token, twitter_access_token_secret)
twitter_client = tweepy.API(auth)

# Function to generate a post using Groq's Chat API (DeepSeek inference)
def generate_post():
    prompt = random.choice(prompts)
    logger.info(f"Generating post with prompt: {prompt}")
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",  # Use the desired DeepSeek model via Groq
            stream=False
        )
        
        generated_text = chat_completion.choices[0].message.content.strip()
        logger.info("Successfully generated post content.")
        
        # Split into title and body (if a newline exists)
        lines = generated_text.split("\n", 1)
        title = lines[0] if len(lines) > 1 else "🔥 FireScan: AI for Wildfire Prevention"
        body = lines[1] if len(lines) > 1 else generated_text
        
        # Remove any markdown and "Title:" prefix from the title
        title = title.strip()
        title = re.sub(r"^\*+\s*title:\s*", "", title, flags=re.IGNORECASE)
        if title.lower().startswith("title:"):
            title = title[len("title:"):].strip()
        
        # Append FireScan link to the body
        firescan_link = "\n\nLearn more at: https://firescan.app/"
        body += firescan_link
        
        logger.info(f"Generated title: {title}")
        logger.info(f"Generated body (first 100 chars): {body[:100]}...")
        
        return title, body
    
    except Exception as e:
        logger.error(f"Error generating post: {e}")
        return "Error generating post", str(e)

# Function to post to Twitter
def post_to_twitter(title, body):
    # For Twitter, we'll tweet the title plus a link to FireScan.
    tweet_text = f"{title}\n\nLearn more at: https://firescan.app/"
    # Ensure tweet_text is within Twitter's 280 character limit:
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."
    try:
        twitter_client.update_status(tweet_text)
        logger.info("✅ Posted to Twitter")
    except Exception as e:
        logger.error(f"Error posting to Twitter: {e}")

# Function to post to Reddit and Twitter
def post_to_social():
    logger.info("Posting to social platforms...")
    title, body = generate_post()
    if "Error" not in title:
        # Post to Reddit
        subreddit.submit(title=title, selftext=body)
        logger.info(f"✅ Posted to Reddit: {title}")
        # Post to Twitter
        post_to_twitter(title, body)
    else:
        logger.warning("Skipping post due to generation error.")

# Run the bot every 8 hours (3 posts per day)
while True:
    try:
        post_to_social()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    time.sleep(8 * 60 * 60)  # 8 hours
