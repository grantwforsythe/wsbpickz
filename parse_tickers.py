#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import praw
from datetime import datetime

reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    user_agent=os.getenv('USER_AGENT'),
)

SUBREDDITS = {
    'wallstreetbets',
    'wallstreetbetsOGs',
    'wallstreetbetsnew',
    'wallstreetbetsELITE'
}

LIMIT = 40

# a text file containing all of the current tickers on the NYSE
with open('data/curated_stock_tickers.txt', 'r') as file:
    TICKERS = {line.strip() for line in file.readlines()}


def parse_subreddit(subreddit, regex = r'[$]? [A-Z]{3,4}'):
    """
    Count the number stocks mentioned in comments across a number of new posts on a subreddit

    :param str subreddit: The subreddit to be parsed
    :param str regex: The expression of interest 
    :param int limit: The number of posts to be parsed
    """
    global num_posts
    global num_comments
    for post in reddit.subreddit(subreddit).new(limit=LIMIT):
        num_posts += 1
        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            num_comments += 1
            for ticker in re.findall(regex, comment.body.strip()):
                if ticker.strip() in TICKERS:
                    stocks[ticker] = stocks.get(ticker, 1) + 1
    
stocks = dict()
num_posts = 0
num_comments = 0 

def main():
    global stocks

    for subreddit in SUBREDDITS:
        parse_subreddit(subreddit)

    # covert to json format
    list_of_stock = [{"ticker": key, "count": value} for key, value in stocks.items()]
    stocks = sorted(list_of_stock, key=lambda item: item['count'], reverse=True)

    obj = {"stocks": stocks, "num_posts": num_posts, "num_comments": num_comments, "datetime": datetime.now().strftime('%B %d %Y at %H:%M EST')}
    with open('data/stocks.json', 'w') as file:
        json.dump(obj, file, indent=4)

if __name__ == '__main__':
    main()