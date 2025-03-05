import praw
import os
import time
import logging
import random
from transformers import pipeline  # Import the pipeline function

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

# Hugging Face model to use for text generation (DeepSeek model)
huggingface_model = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"  # Use DeepSeek model

# Initialize the Hugging Face pipeline
pipe = pipeline("text-generation", model=huggingface_model)

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

# Function to generate a wildfire-related post using Hugging Face API (via pipeline)
def generate_post():
    prompt = random.choice(prompts)  # Select a random prompt
    logger.info(f"Generating post with prompt: {prompt}")

    # Use the pipeline to generate text based on the prompt
    generated_content = pipe(prompt)[0]['generated_text']
    logger.info(f"Successfully generated post content: {generated_content[:100]}...")  # Log the start of the content for brevity

    # Split the response into title & body
    lines = generated_content.split("\n", 1)
    title = lines[0] if len(lines) > 1 else "🔥 FireScan: AI for Wildfire Prevention"
    body = lines[1] if len(lines) > 1 else generated_content

    logger.info(f"Generated title: {title}")
    logger.info(f"Generated body: {body[:100]}...")  # Log the start of the body for brevity

    return title, body

# Function to submit a post
def post_to_reddit():
    logger.info("Posting to Reddit...")
    title, body = generate_post()
    subreddit.submit(title=title, selftext=body)
    logger.info(f"✅ Posted: {title}")

# Run the bot 3 times a day
while True:
    try:
        post_to_reddit()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    time.sleep(8 * 60 * 60)  # Wait 8 hours (8 hours * 60 min * 60 sec)
