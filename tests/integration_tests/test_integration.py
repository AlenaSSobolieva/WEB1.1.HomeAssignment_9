import unittest
from unittest.mock import patch
from io import StringIO
from scraping import get_quotes_and_authors, upload_to_mongodb
from search_quotes import main
from mongoengine import connect, disconnect
from pymongo import MongoClient
from classes import Author, Quote


class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Connect to the test database
        connect(
            db='test_db',
            alias='default',
            username='soboleva13as',
            password='5413034002246',
            host='mongodb+srv://soboleva13as:5413034002246@cluster0.xpt2wff.mongodb.net/web8'
        )

    @classmethod
    def tearDownClass(cls):
        # Disconnect from MongoDB and drop the test database
        disconnect()
        connection = Author._get_db().client
        connection.drop_database('test_db')

    def test_integration(self):
        # Test the integration of get_quotes_and_authors, upload_to_mongodb, and search_quotes
        base_url = 'http://quotes.toscrape.com'
        all_quotes, all_authors = get_quotes_and_authors(base_url)

        # Capture stdout for the main function
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('main.search_quotes.input', side_effect=['exit']):  # Simulate user input
                upload_to_mongodb(all_quotes, all_authors)
                main()

                # Capture the output of the search_quotes script
                main()

                # Check if expected output is present in the captured stdout
                self.assertIn("Script execution ended.", mock_stdout.getvalue())
                self.assertIn("Pinged MongoDB using pymongo. Connection successful!", mock_stdout.getvalue())

                # Verify that data is present in the test database
                self.assertGreater(Author.objects().count(), 0)
                self.assertGreater(Quote.objects().count(), 0)


if __name__ == '__main__':
    unittest.main()
