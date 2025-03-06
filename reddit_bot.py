import praw
import os
import time
import logging
import random
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
    user_agent="firescan_llama2_bot"
)

# Target subreddit
subreddit = reddit.subreddit("wildfire")

# List of prompts for variety
prompts = [
    "Write a Reddit post about a recent wildfire, its impact, and how FireScan helps detect and mitigate wildfires using AI-powered drones. FireScan integrates multiple satellite data sources for early wildfire detection and prediction, providing real-time insights to firefighters.",
    "How can AI-powered systems like FireScan prevent wildfires before they get out of control? Write a discussion post about the role of AI in early wildfire detection, using real-time satellite data and predictive models.",
    "FireScan is an AI-driven wildfire detection and response system. It integrates multiple satellite sources, advanced sensing capabilities, and autonomous drone deployment to help firefighters combat wildfires effectively. Write a Reddit post discussing how this technology can transform wildfire management.",
    "A wildfire broke out in [insert location]. FireScan, an AI-driven wildfire detection platform, provided early warnings that helped firefighters deploy resources efficiently. Write a news-style Reddit post discussing how AI and drones improve wildfire response times.",
    "Wildfires are becoming more frequent and severe. FireScan acts as a community fire reporting tool, quickly alerting authorities as AI processes multiple data sources for early detection. Write a Reddit discussion post about the importance of rapid wildfire reporting."
]

# Hugging Face Inference API endpoint for LLaMA2 Chat model
# (Here we use the 7B chat variant; adjust model_id as needed.)
MODEL_ID = "meta-llama/Llama-2-7b-chat-hf"
HF_API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Function to generate a post using LLaMA2 via Hugging Face Inference API
def generate_post():
    prompt = random.choice(prompts)
    logger.info(f"Generating post with prompt: {prompt}")
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    
    # For a chat model, you can include a chat-like context.
    # Here we simply send the prompt as input.
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            error_msg = f"Error code: {response.status_code} - {response.json()}"
            logger.error(error_msg)
            return "Error generating post", error_msg
        
        result = response.json()
        # The Hugging Face API for text generation returns a list.
        # We assume the first item contains our generated text.
        generated_text = result[0]["generated_text"].strip()
        logger.info("Successfully generated post content.")
        
        # Split into title and body (if newline exists)
        lines = generated_text.split("\n", 1)
        title = lines[0] if len(lines) > 1 else "🔥 FireScan: AI for Wildfire Prevention"
        body = lines[1] if len(lines) > 1 else generated_text
        
        logger.info(f"Generated title: {title}")
        logger.info(f"Generated body (first 100 chars): {body[:100]}...")
        
        return title, body
    
    except Exception as e:
        logger.error(f"Error generating post: {e}")
        return "Error generating post", str(e)

def post_to_reddit():
    logger.info("Posting to Reddit...")
    title, body = generate_post()
    if "Error" not in title:
        subreddit.submit(title=title, selftext=body)
        logger.info(f"✅ Posted: {title}")
    else:
        logger.warning("Skipping post due to generation error.")

# Run the bot every 8 hours (3 posts per day)
while True:
    try:
        post_to_reddit()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    time.sleep(8 * 60 * 60)  # 8 hours
