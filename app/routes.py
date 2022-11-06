import json
from app import app
from flask import render_template


SUBREDDITS = (
    'wallstreetbets',
    'wallstreetbetsOGs',
    'wallstreetbetsnew',
    'wallstreetbetsELITE'
)

@app.route("/")
def index():
    with open('data/stocks.json', 'r') as f:
        stocks = json.load(f)

    return render_template(
        'index.html', 
        stocks=stocks,
        subreddits=SUBREDDITS
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404