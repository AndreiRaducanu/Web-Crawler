import scrapy
from bs4 import BeautifulSoup
import json

class TokenSpider(scrapy.Spider):
    name = 'token'
    start_urls = [
        'https://www.storia.ro/ro/rezultate/inchiriere/apartament/bucuresti?market=ALL&ownerTypeSingleSelect=ALL&distanceRadius=0&viewType=listing'
    ]

    # Define the user agent in custom settings
    custom_settings = {
    'USER_AGENT': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    ),
}

    # Initialize build_id as None
    build_id = None

    def parse(self, response):
        # Extract data from the response
        html_content = response.body

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the element with the ID "__NEXT_DATA__"
        next_data_element = soup.find(id='__NEXT_DATA__')

        if next_data_element:
            # Extract & Parse the content of the element
            element_content = next_data_element.text.strip()
            json_data = json.loads(element_content)
            build_id = json_data.get('buildId')
            TokenSpider.build_id = build_id

            yield {
                'buildId': build_id
            }
        else:
            self.logger.warning("Element with ID '__NEXT_DATA__' not found in the HTML response.")
