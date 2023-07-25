from flask import Flask, render_template
import feedparser
import bleach
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

RSS_FEED_URL = "https://www.journalduhacker.net/rss"

PLACEHOLDER_IMAGE_URL = "https://www.savoirscom1.info/wp-content/uploads/2013/07/logo-rss_icone.png"


@app.route('/')
def index():
    feed = feedparser.parse(RSS_FEED_URL)
    entries = feed.entries
    entries_by_date = group_entries_by_date(entries)
    return render_template('index.html', entries_by_date=entries_by_date)

def group_entries_by_date(entries):
    entries_by_date = defaultdict(list)
    for entry in entries:
        entry.summary = bleach.clean(entry.summary, tags=['b', 'i', 'a'], attributes={'a': ['href']}, strip=True)
        entry.image_url = get_article_image(entry.link)
        published_date = parse_date(entry.published)
        entries_by_date[published_date].append(entry)
    return entries_by_date

def parse_date(date_str):
    return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")



def is_image_accessible(url):
    response = requests.head(url)
    return response.status_code == 200 and response.headers.get('content-type', '').startswith('image')


def get_article_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        img_tags = soup.find_all('img')
        if img_tags:
            image_url = img_tags[0]['src']
            if not image_url.startswith('http'):
                image_url = f"{url.rstrip('/')}/{image_url.lstrip('/')}"
            if is_image_accessible(image_url):
                # return image_url # --> uncomment this to return the scraped images if available
                return PLACEHOLDER_IMAGE_URL  # --> and comment this one
    return PLACEHOLDER_IMAGE_URL


if __name__ == '__main__':
    app.run(debug=True)
