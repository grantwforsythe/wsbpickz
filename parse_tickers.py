#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import praw
import functools
import numpy as np
import pandas as pd
from datetime import datetime


# create client
reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    user_agent=os.getenv('USER_AGENT'),
)

# subreddits to be parsed
SUBREDDITS = {
    'wallstreetbets',
    'wallstreetbetsOGs',
    'wallstreetbetsnew',
    'wallstreetbetsELITE'
}

# number of posts
LIMIT = 40

# parse tickers from text file
with open('data/curated_stock_tickers.txt', 'r') as file:
    TICKERS = {line.strip() for line in file.readlines()}


def main():
    regex = r'[$]? [A-Z]{3,4}'

    dfs = [
        parse_subreddit(subreddit, regex)
        for subreddit in SUBREDDITS
    ]

    # add the DataFrames together
    df = functools.reduce(pd.DataFrame.add, dfs)
    # save the results to a json file
    df[df['count'] != 0].sort_values(
        by=['count'],
        ascending=False
    ).to_json(
        os.path.join(os.path.dirname(__file__), 'data', 'stocks.json'),
        orient='index',
        indent=4
    )

def parse_subreddit(subreddit: str, regex: str) -> pd.DataFrame:
    """
    Count the number stocks mentioned in comments across a number of hot posts on a subreddit.

    :param str subreddit: The subreddit to be parsed
    :param str regex: The regular expression to match
    :return: A DataFrame of the frequency of stock tickers
    """
    df = pd.DataFrame(
        data=0,
        index=pd.Index(TICKERS, name='ticker'),
        columns=['count'],
        dtype=np.int32
    )

    for post in reddit.subreddit(subreddit).new(limit=LIMIT):
        # remove MoreComments object(s)
        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            for ticker in re.findall(regex, comment.body.strip()):
                try:
                    df.loc[ticker.strip()] += 1
                except KeyError:
                    # We only care about tickers that recognize
                    pass
    return df
    

if __name__ == '__main__':
    print('Starting...')

    try:
        main()
    except KeyboardInterrupt:
        print('Interupted')
    finally:
        print('Fini')