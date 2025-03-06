import praw
import os
import time
import logging
import random
from openai import OpenAI  # Import the new OpenAI client class

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

# Instantiate the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def generate_post():
    prompt = random.choice(prompts)
    logger.info(f"Generating post with prompt: {prompt}")

    try:
        # Use the new client-based method for chat completions
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or use "gpt-3.5-turbo" if preferred
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )

        # Access the content from the Pydantic model response
        content = response.choices[0].message.content.strip()
        logger.info("Successfully generated post content.")

        # Split response into title and body (if applicable)
        lines = content.split("\n", 1)
        title = lines[0] if len(lines) > 1 else "🔥 FireScan: AI for Wildfire Prevention"
        body = lines[1] if len(lines) > 1 else content

        logger.info(f"Generated title: {title}")
        logger.info(f"Generated body: {body[:100]}...")  # Log the beginning of the body for brevity

        return title, body

    except Exception as e:
        logger.error(f"Error generating post: {e}")
        return "Error generating post", "Please try again later"

def post_to_reddit():
    logger.info("Posting to Reddit...")
    title, body = generate_post()
    if "Error" not in title:  # Avoid posting if there was an error
        subreddit.submit(title=title, selftext=body)
        logger.info(f"✅ Posted: {title}")
    else:
        logger.warning("Skipping post due to generation error.")

# Run the bot every 8 hours (3 times per day)
while True:
    try:
        post_to_reddit()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    time.sleep(8 * 60 * 60)  # Sleep for 8 hours
