"""
Mallory Rich
IS 303

Quotes Collection - text data analysis

INPUT: 
- quotes.toscrape.com (3 pages)
# div class = quote
# span class = text
# span small class = author
# div class = tags

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
import sqlite3

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


def scrape_all_pages(base_url):
    # Scrape multiple pages
    pages_url = [base_url, base_url + "/page/2/", base_url + "/page/3/"]

    for page_url in pages_url:
        print(f"\nScraping {page_url}...")
        quote_data = parse_page(page_url)
        
        for quote in quote_data:
            store_quote(quote)
        
        time.sleep(5)  # Be respectful to the server


def query_analyze():
    connect = sqlite3.connect("quotes.db")
    df = pd.read_sql("SELECT * FROM quote", connect)

    # quotes per author
    print("\nQuotes per Author:")
    quotes_per_author = (df.groupby("author").size().sort_values(ascending=False))
    print(quotes_per_author)

    # most prolific artists
    print("\nMost Prolific Authors:")
    print(df.groupby("author").size().nlargest(5)) 

    # tag frequency
    print("\nTag Frequency:")
    all_tags = []
    for tag in df["tags"]:
        all_tags.extend(tag.split(", "))
    tag_df = pd.DataFrame({"tag": all_tags})
    print(tag_df.groupby("tag").size().sort_values(ascending=False))
    
    return quotes_per_author


def data_visualization(quotes_per_author):
    plt.figure(figsize=(10, 6))
    plt.bar(quotes_per_author.index, quotes_per_author.values, color="purple")
    plt.title("Quotes per Author")
    plt.xlabel("Authors")
    plt.ylabel("# of Quotes")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig("quotes_per_author.png")
    plt.show()


def main(base_url):
    scrape_all_pages(base_url)
    quotes_per_author = query_analyze()
    data_visualization(quotes_per_author)

main("http://quotes.toscrape.com")