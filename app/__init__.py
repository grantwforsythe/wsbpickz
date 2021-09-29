import os
import praw
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    user_agent=os.getenv('USER_AGENT'),
)

app = Flask(__name__)

from app import routes