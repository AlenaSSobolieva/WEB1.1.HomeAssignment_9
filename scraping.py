import requests
from bs4 import BeautifulSoup
from mongoengine import StringField, ListField, ReferenceField, Document, connect
from pymongo import MongoClient
import json

class Author(Document):
    fullname = StringField()
    born_date = StringField()
    born_location = StringField()
    description = StringField()

class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author, reverse_delete_rule=True)
    quote = StringField()

def get_quotes_and_authors(base_url):
    quotes_url = '/page/{}/'
    all_quotes = []
    all_authors = []

    page_number = 1
    while True:
        page_url = base_url + quotes_url.format(page_number)
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        quotes = []
        for quote in soup.select('div.quote'):
            quote_text = quote.find('span', class_='text').get_text(strip=True)
            author_name = quote.find('small', class_='author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote.select('div.tags a.tag')]

            quotes.append({'tags': tags, 'author': author_name, 'quote': quote_text})

            # Extract author information
            if author_name not in all_authors:
                author_url = base_url + f'/author/{author_name.lower().replace(" ", "-")}/'
                author_info = get_author_info(author_url)
                all_authors.append(author_info)

        if not quotes:
            break

        all_quotes.extend(quotes)
        page_number += 1

    return all_quotes, all_authors

def get_author_info(author_url):
    response = requests.get(author_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    fullname_elem = soup.find('span', class_='author-title')
    born_date_elem = soup.find('span', class_='author-born-date')
    born_location_elem = soup.find('span', class_='author-born-location')
    description_elem = soup.find('div', class_='author-description')

    fullname = fullname_elem.get_text(strip=True) if fullname_elem else None
    born_date = born_date_elem.get_text(strip=True) if born_date_elem else None
    born_location = born_location_elem.get_text(strip=True) if born_location_elem else None
    description = description_elem.get_text(strip=True) if description_elem else None

    author_info = {
        'fullname': fullname,
        'born_date': born_date,
        'born_location': born_location,
        'description': description
    }

    return author_info

def upload_to_mongodb(all_quotes, all_authors):
    connection_string = 'mongodb+srv://soboleva13as:5413034002246@cluster0.xpt2wff.mongodb.net/web8'

    # Check the connection using pymongo
    try:
        pymongo_client = MongoClient(connection_string)
        pymongo_client.admin.command('ping')
        print("Pinged MongoDB using pymongo. Connection successful!")
    except Exception as e:
        print("Error connecting to MongoDB using pymongo:", e)

    # Connect using mongoengine
    connect(db='web-8', username='soboleva13as', password='5413034002246',
            host='mongodb+srv://soboleva13as:5413034002246@cluster0.xpt2wff.mongodb.net/web8')

    # Store data in MongoDB
    for author_info in all_authors:
        # Check if 'fullname' is present in author_info
        if 'fullname' in author_info:
            author = Author(**author_info)
            author.save()

    for quote_data in all_quotes:
        # Check if 'author' is present in quote_data
        if 'author' in quote_data:
            author = Author.objects(fullname=quote_data['author']).first()
            del quote_data['author']
            quote = Quote(author=author, **quote_data)
            quote.save()

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