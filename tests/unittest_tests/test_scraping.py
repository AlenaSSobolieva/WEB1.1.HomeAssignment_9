import unittest
from unittest.mock import patch, Mock
from io import StringIO
from mongoengine import connect, disconnect
from scraping import Author, Quote, get_quotes_and_authors, upload_to_mongodb, get_author_info

class TestScraping(unittest.TestCase):

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
        # Disconnect explicitly from the test database
        disconnect(alias='default')

    def setUp(self):
        # Mocking the response
        base_url = 'http://quotes.toscrape.com'
        quotes_url = '/page/{}/'

        mock_response = Mock()
        mock_response.text = """
            <div class="quote">
                <span class="text">Quote Text 1</span>
                <small class="author">Author 1</small>
                <div class="tags"><a class="tag">Tag1</a></div>
            </div>
            <div class="quote">
                <span class="text">Quote Text 2</span>
                <small class="author">Author 2</small>
                <div class="tags"><a class="tag">Tag2</a></div>
            </div>
        """

        with patch('scraping.requests.get', return_value=mock_response):
            with patch('scraping.get_author_info', return_value={'fullname': 'Author 1'}):
                # Call the function
                all_quotes, all_authors = get_quotes_and_authors(base_url)

        # Store data in MongoDB
        for author_info in all_authors:
            author = Author(**author_info)
            author.save()

        for quote_data in all_quotes:
            author = Author.objects(fullname=quote_data['author']).first()
            if 'author' in quote_data:
                del quote_data['author']  # Remove 'author' key if present
            quote = Quote(author=author, **quote_data)
            quote.save()

    def tearDown(self):
        # Clear the data in the test database after each test
        connection = Author._get_db().client
        connection.drop_database('test_db')

    @patch('builtins.input', side_effect=['name:Author 1', 'exit'])
    def test_search_by_name(self, mock_input):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # You need to call your search function here
            # Example: search_quotes_by_name('Author 1')
            output = mock_stdout.getvalue()
            self.assertIn("Author 1:", output)
            self.assertIn("Quote Text 1", output)

    @patch('builtins.input', side_effect=['tag:Tag1', 'exit'])
    def test_search_by_tag(self, mock_input):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Call your search function here
            # Example: search_quotes_by_tag('Tag1')
            output = mock_stdout.getvalue()
            self.assertIn("Author 1:", output)
            self.assertIn("Quote Text 1", output)

    @patch('scraping.requests.get')  # Mock the requests.get method
    def test_get_quotes_and_authors(self, mock_get):
        # Mock the response from requests.get
        mock_response = Mock()
        mock_response.text = """
            <div class="quote">
                <span class="text">Quote Text 3</span>
                <small class="author">Author 3</small>
                <div class="tags"><a class="tag">Tag3</a></div>
            </div>
            <div class="quote">
                <span class="text">Quote Text 4</span>
                <small class="author">Author 4</small>
                <div class="tags"><a class="tag">Tag4</a></div>
            </div>
        """
        mock_get.return_value = mock_response

        base_url = 'http://quotes.toscrape.com'
        quotes_url = '/page/{}/'

        # Call the function
        all_quotes, all_authors = get_quotes_and_authors(base_url)

        # Your assertions based on the mocked response
        self.assertEqual(len(all_quotes), 2)
        self.assertEqual(len(all_authors), 2)

        # Add more assertions based on the expected behavior of your code

if __name__ == '__main__':
    unittest.main()
