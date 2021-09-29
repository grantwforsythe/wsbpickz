import re
import json
from app import app, reddit
from flask import render_template
from datetime import datetime

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('app.log')
logger.addHandler(file_handler)

# subreddits to be parsed
SUBREDDITS = (
    'wallstreetbets',
    'wallstreetbetsOGs',
    'wallstreetbetsnew',
    'wallstreetbetsELITE'
)

# a text file containing all of the current tickers on the NYSE
with open('curated_stock_tickers.txt', 'r') as f:
    TICKERS = set([line.strip() for line in f.readlines()])

stocks = dict()


def parse_subreddit(subreddit, regex = r'[$]? [A-Z]{3,4}', limit = 10) -> None:
    """
    Count the number stocks mentioned in comments across a number of new posts on a subreddit

    :param str subreddit: The subreddit to be parsed
    :param str regex: The expression of interest 
    :param int limit: The number of posts to be parsed
    """
    num_posts = 0
    num_comments = 0
    for post in reddit.subreddit(subreddit).new(limit=limit):
        num_posts += 1
        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            num_comments += 1
            for ticker in re.findall(regex, comment.body.strip()):
                if ticker.strip() in TICKERS:
                    stocks[ticker] = stocks.get(ticker, 1) + 1
    
    return num_posts, num_comments


num_posts = 0
num_comments = 0

logger.info('Starting app.')
for subreddit in SUBREDDITS:
    logger.info(f'Parsing r\{subreddit}')
    x, y = parse_subreddit(subreddit, limit=5)
    num_posts += x
    num_comments += y

# source: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
stocks = dict(sorted(stocks.items(), key=lambda item: item[1], reverse=True))

items = {"stocks": stocks, "num_posts": num_posts, "num_comments": num_comments, "datetime": datetime.now().strftime('%B %d %Y at %H:%M EST')}
with open('stocks.json', 'w') as f:
    json.dump(items, f, indent=4)

print('Created json file')
logger.info('App is online.')


@app.route("/")
def index():
    with open('stocks.json', 'r') as f:
        stocks = json.load(f)

    return render_template(
        'index.html', 
        stocks=stocks['stocks'],
        subreddits=SUBREDDITS,
        num_comments=stocks['num_comments'],
        num_posts=stocks['num_posts'],
        date_time=stocks['datetime']
    )