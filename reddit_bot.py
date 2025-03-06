import praw
import os
import time
import logging
import random
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reddit API authentication
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    user_agent="fire_scan_bot"
)

# OpenAI API Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Target subreddit
subreddit = reddit.subreddit("wildfire")

# List of prompts for variety
prompts = [
    "Write a compelling Reddit post about a recent wildfire and how FireScan's AI-driven detection system helped mitigate its impact.",
    "How can AI-powered systems like FireScan prevent wildfires before they get out of control? Write a discussion post explaining how FireScan integrates real-time satellite data.",
    "FireScan is an AI-driven wildfire detection and response system. It integrates multiple satellite sources, advanced sensing capabilities, and autonomous drone deployment to help firefighters combat wildfires effectively. Write a Reddit post discussing how this technology can transform wildfire management.",
    "A wildfire broke out in [insert location]. FireScan, an AI-driven wildfire detection platform, provided early warnings, helping firefighters deploy resources efficiently. Write a news-style Reddit post about AI improving wildfire response times.",
    "Wildfires are increasing in frequency. FireScan acts as a community fire reporting tool, allowing people to quickly report fires while AI processes multiple data sources for accurate early detection. Write a Reddit discussion post on AI in wildfire prevention."
]

# Function to generate a wildfire-related post using OpenAI
def generate_post():
    prompt = random.choice(prompts)  # Select a random prompt
    logger.info(f"Generating post with prompt: {prompt}")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in wildfire prevention and AI-based disaster management. Generate engaging Reddit posts on these topics."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()

        if content.startswith(prompt):  # If it echoes the prompt, retry
            logger.warning("Generated content is too similar to the prompt. Retrying...")
            return generate_post()

        logger.info("Successfully generated post content.")

        # Split content into title & body
        lines = content.split("\n", 1)
        title = lines[0] if len(lines) > 1 else "🔥 FireScan: AI for Wildfire Prevention"
        body = lines[1] if len(lines) > 1 else content

        logger.info(f"Generated title: {title}")
        logger.info(f"Generated body preview: {body[:100]}...")  # Log only the start for brevity

        return title, body

    except Exception as e:
        logger.error(f"Error generating post: {e}")
        return "Error generating post", "Please try again later."

# Function to submit a post
def post_to_reddit():
    logger.info("Posting to Reddit...")
    title, body = generate_post()
    
    if "Error" not in title:  # Avoid posting error messages
        subreddit.submit(title=title, selftext=body)
        logger.info(f"✅ Posted successfully: {title}")
    else:
        logger.warning("Skipping post due to generation error.")

# Run the bot every 8 hours
while True:
    try:
        post_to_reddit()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    time.sleep(8 * 60 * 60)  # Wait 8 hours before posting again
