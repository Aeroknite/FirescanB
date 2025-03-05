import praw
import os
import time
import random
from transformers import GPTJForCausalLM, GPT2Tokenizer
import torch

# Reddit API authentication
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    user_agent="fire_scan_bot"
)

# Load the GPT-J model and tokenizer from Hugging Face
model_name = "EleutherAI/gpt-j-6B"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTJForCausalLM.from_pretrained(model_name)

# Target subreddit
subreddit = reddit.subreddit("wildfire")

# Function to generate a wildfire-related post using GPT-J
def generate_post():
    prompt = "Write a Reddit post about a recent wildfire, its impact, and how FireScan helps detect and mitigate wildfires using AI-powered drones."
    
    # Encode the prompt and generate a response using GPT-J
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs['input_ids'], max_length=250, num_return_sequences=1, no_repeat_ngram_size=2, top_p=0.95, temperature=0.7)

    # Decode the output and split it into title and body
    content = tokenizer.decode(outputs[0], skip_special_tokens=True)

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
