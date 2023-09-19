import scrapy
import json
from datetime import datetime
import time

class JsonSpider(scrapy.Spider):
    name = 'json_spider'
    json_data = None

    def __init__(self, page, token):
        self.page = int(page)  # Convert page to an integer
        self.token = token
        self.base_url = 'https://www.storia.ro/_next/data/' + self.token + '/ro/rezultate/inchiriere/apartament/bucuresti.json'
    
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
            items_page = len(json_data['pageProps']['data']['searchAds']['items'])
            print(f'Items in page: {str(items_page)}')
            time.sleep(3)
            items = json_data['pageProps']['data']['searchAds']['items']
            date_key = "dateCreated"
            date_list = []
            for dict in items:
                date_list.append(dict[date_key])
        
            page_date_str = (date_list[len(date_list)-1])  # last date from page
            page_date = datetime.strptime(page_date_str, '%Y-%m-%d %H:%M:%S')
            today = datetime.today()
            result_day = today.day - page_date.day
            print(f'Page_date: {page_date.day}\n')
            print(f'Result day: {result_day}')
            
            if result_day == 0:
                # Increment the page number and run the Spider again
                with open(f'output_page_{self.page}.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
                self.page += 1
                next_page_url = response.url.split('&page=')[0] + f'&page={self.page}'
                yield response.follow(next_page_url, self.parse)
            else:
                # Save JSON data to a file
                with open(f'output_page_{self.page}.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            
                yield {
                    'json_data': json_data
                }
        else:
            self.logger.warning(f'Invalid content type: {content_type}')
