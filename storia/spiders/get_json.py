import scrapy
import json

class JsonSpider(scrapy.Spider):
    name = 'json_spider'
    json_data = None

    def __init__(self, page, token):
        self.page = page
        self.token = token
        self.base_url = 'https://www.storia.ro/_next/data/' + self.token + '/ro/rezultate/inchiriere/apartament/bucuresti.json'
    
    # Define the base URL without the page number

    # Define the custom query string
    custom_query = {
        "market": "ALL",
        "ownerTypeSingleSelect": "ALL",
        "distanceRadius": "0",
        "viewType": "listing",
        "searchingCriteria": ["inchiriere", "apartament", "bucuresti"]
    }
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    def start_requests(self):
        # You can specify the page number as an argument when running the Spider
        
        
        # Update the custom query with the page number
        self.custom_query['page'] = str(self.page)
        
        # Construct the full URL with the custom query string
        query_string = '&'.join([f'{key}={value}' for key, value in self.custom_query.items()])
        url = f'{self.base_url}?{query_string}'
        
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        if 'application/json' in content_type:
            # Parse the JSON content
            json_data = response.json()
            JsonSpider.json_data = json_data
            
            # Save JSON data to a file
            with open(f'data/output_page_{self.custom_query["page"]}.json', 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            
            yield {
                'json_data': json_data
            }
        else:
            self.logger.warning(f'Invalid content type: {content_type}')