import praw
import os
import time
import logging
from transformers import GPT2LMHeadModel, GPT2Tokenizer  # Smaller model (GPT-2)
import requests

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

# Hugging Face API token (set this in Railway environment variables)
huggingface_api_token = os.getenv("HF_API_KEY")
huggingface_model = "gpt2"  # Using GPT-2, a smaller model

# Target subreddit
subreddit = reddit.subreddit("wildfire")

# Function to generate a wildfire-related post using Hugging Face API
def generate_post():
    prompt = "Write a Reddit post about a recent wildfire, its impact, and how FireScan helps detect and mitigate wildfires using AI-powered drones."

    logger.info("Generating post using Hugging Face API...")

    # Call Hugging Face API to generate the text
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{huggingface_model}",
        headers={"Authorization": f"Bearer {huggingface_api_token}"},
        json={"inputs": prompt}
    )
    
    if response.status_code == 200:
        content = response.json()[0]['generated_text']
        logger.info("Successfully generated post content.")
    else:
        logger.error(f"Error generating post: {response.status_code}, {response.text}")
        return "Error generating post", "Please try again later"

    # Split the response into title & body
    lines = content.split("\n", 1)
    title = lines[0] if len(lines) > 1 else "🔥 FireScan: The Future of Wildfire Prevention"
    body = lines[1] if len(lines) > 1 else content

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
