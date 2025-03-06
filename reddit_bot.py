import praw
import os
import time
import logging
import random
import openai  # ✅ Corrected OpenAI import

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

# OpenAI API key (set this in Railway environment variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Target subreddit
subreddit = reddit.subreddit("wildfire")

# List of prompts for variety
prompts = [
    "Write a Reddit post about a recent wildfire, its impact, and how FireScan helps detect and mitigate wildfires using AI-powered drones. FireScan integrates multiple satellite data sources for early wildfire detection and prediction, providing real-time insights to firefighters.",
    "How can AI-powered systems like FireScan prevent wildfires before they get out of control? Write a discussion post about the role of AI in early wildfire detection, using real-time satellite data and predictive models.",
    "FireScan is an AI-driven wildfire detection and response system. It integrates multiple satellite sources, advanced sensing capabilities, and autonomous drone deployment to help firefighters combat wildfires effectively. Write a Reddit post discussing how this technology can transform wildfire management.",
    "A wildfire broke out in [insert location]. FireScan, an AI-driven wildfire detection platform, was able to provide early warnings, helping firefighters deploy resources efficiently. Write a news-style Reddit post discussing how AI and drones can improve wildfire response times.",
    "Wildfires are becoming more frequent and severe. FireScan acts as a community fire reporting tool, allowing people to quickly report fires while AI processes multiple data sources for accurate early detection. How can AI-powered platforms like FireScan empower local communities? Write a Reddit discussion post."
]

# Function to generate a wildfire-related post using OpenAI GPT-3.5/4
def generate_post():
    prompt = random.choice(prompts)  # Select a random prompt
    logger.info(f"Generating post with prompt: {prompt}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-4 if needed
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )

        content = response["choices"][0]["message"]["content"].strip()
        logger.info("Successfully generated post content.")

        # Split the response into title & body
        lines = content.split("\n", 1)
        title = lines[0] if len(lines) > 1 else "🔥 FireScan: AI for Wildfire Prevention"
        body = lines[1] if len(lines) > 1 else content

        logger.info(f"Generated title: {title}")
        logger.info(f"Generated body: {body[:100]}...")  # Log the start of the body for brevity

        return title, body

    except Exception as e:
        logger.error(f"Error generating post: {e}")
        return "Error generating post", "Please try again later"

# Function to submit a post
def post_to_reddit():
    logger.info("Posting to Reddit...")
    title, body = generate_post()
    if "Error" not in title:  # Avoid posting error messages
        subreddit.submit(title=title, selftext=body)
        logger.info(f"✅ Posted: {title}")
    else:
        logger.warning("Skipping post due to generation error.")

# Run the bot 3 times a day
while True:
    try:
        post_to_reddit()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    time.sleep(8 * 60 * 60)  # Wait 8 hours (8 hours * 60 min * 60 sec)
