"""
Mallory Rich
IS 303

Quotes Collection - text data analysis

INPUT: 
- quotes.toscrape.com (3 pages)

PROCESSES:
- fetch data
- scrape url
- store in SQLite (peewee)
- query (pandas)
- analyze
    - Quotes per author
    - tag frequency
    - most prolific authors
- visualize (chart)

OUTPUTS:
- printed analysis
- chart file
- quotes.db

"""
from bs4 import BeautifulSoup
from peewee import SqliteDatabase, Model, CharField, IntegerField
import matplotlib.pyplot as plt
import pandas as pd
import requests, time

db = SqliteDatabase("quotes.db")

class Quote(Model):
    text = CharField()
    author = CharField()
    tags = CharField()

    class Meta:
        database = db

db.connect()
db.create_tables([Quote])

def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        print(f"Failed to fetch {url}: status {response.status_code}")
        return None

def parse_page(url):
    soup = fetch_page(url)
    quotes = soup.find_all("div", class_="quote")

    parsed_quotes = []

    for quote in quotes:
        text = quote.find("span", class_="text")
        author = quote.find("small", class_="author")
        tags_html = quote.find_all("a", class_="tag")
        tags = []
        for tag in tags_html:
            tags.append(tag.text)

        parsed_quotes.append({
            "text":text.text,
            "author": author.text,
            "tags": ", ".join(tags)})
        # print(text.text, author.text, tags)
    return(parsed_quotes)

def store_quote(data):
    existing = Quote.get_or_none(
        (Quote.text == data["text"]) &
        (Quote.author == data["author"]) &
        (Quote.tags == data["tags"])
        )
    
    if existing:
        print(f"Skipping {data['author']}")
        return
    
    Quote.create(**data)
    print(f"Stored {data['author']}")


quote_data = parse_page("http://quotes.toscrape.com")

for quote in quote_data:
    store_quote(quote)



# div class = quote
# span class = text
# span small class = author
# div class = tags

# def main(url):
#     fetch_page(url)




