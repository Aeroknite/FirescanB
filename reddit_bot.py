import praw
import os
import time
import openai
import random

# Reddit API authentication
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    user_agent="fire_scan_bot"
)

# OpenAI API Key (set this in Railway environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Target subreddit
subreddit = reddit.subreddit("wildfire")

# Function to generate a wildfire-related post using OpenAI
def generate_post():
    prompt = "Write a Reddit post about a recent wildfire, its impact, and how FireScan helps detect and mitigate wildfires using AI-powered drones."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if available
        messages=[{"role": "system", "content": prompt}],
        max_tokens=250
    )

    content = response["choices"][0]["message"]["content"]
    
    # Split the response into title & body
    lines = content.split("\n", 1)
    title = lines[0] if len(lines) > 1 else "🔥 FireScan: The Future of Wildfire Prevention"
    body = lines[1] if len(lines) > 1 else content

    return title, body

# Function to submit a post
def post_to_reddit():
    title, body = generate_post()
    subreddit.submit(title=title, selftext=body)
    print(f"✅ Posted: {title}")

# Run the bot 3 times a day
while True:
    post_to_reddit()
    time.sleep(8 * 60 * 60)  # Wait 8 hours (8 hours * 60 min * 60 sec)
