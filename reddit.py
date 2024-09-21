import asyncpraw
import random

from dotenv import load_dotenv  # .env
import os 

load_dotenv()

async def get_image():
    async with asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"), 
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"), 
    ) as reddit:
      
        subreddit = await reddit.subreddit(os.getenv("PERSONAL_SUBREDDIT"))
        random_post = random.choice([random_post async for random_post in subreddit.hot(limit=100)])
          
        random_color = random.randint(0, 0xFFFFFF)
        return random_post.url, random_post.title, random_color
