from mongoengine import Document, StringField, ListField, ReferenceField, connect
from pymongo import MongoClient
import json
from scraping import get_quotes_and_authors, upload_to_mongodb

class Author(Document):
    fullname = StringField()
    born_date = StringField()
    born_location = StringField()
    description = StringField()

class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author, reverse_delete_rule=True)
    quote = StringField()

def main():
    base_url = 'http://quotes.toscrape.com'
    all_quotes, all_authors = get_quotes_and_authors(base_url)

    with open('quotes.json', 'w', encoding='utf-8') as quotes_file:
        json.dump(all_quotes, quotes_file, ensure_ascii=False, indent=2)

    with open('authors.json', 'w', encoding='utf-8') as authors_file:
        json.dump(all_authors, authors_file, ensure_ascii=False, indent=2)

    upload_to_mongodb(all_quotes, all_authors)

if __name__ == '__main__':
    main()
