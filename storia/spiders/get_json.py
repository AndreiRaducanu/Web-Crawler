import scrapy
import json
from datetime import datetime
import time
import pandas as pd

class JsonSpider(scrapy.Spider):
    name = 'json_spider'
    json_data = []

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
            items_page = len(json_data['pageProps']['data']['searchAds']['items'])
            print(f'Items in page: {str(items_page)}')
            time.sleep(0.3)
            offer_data = []  # DataFrames
            for offer in json_data['pageProps']['data']['searchAds']['items']:
                try:
                    offer_id = offer['id']
                    title = offer['title']
                    slug = offer['slug']
                    area = offer['areaInSquareMeters']
                    rooms = offer['roomsNumber']
                    date = offer['dateCreated']
                    location = offer['location']['reverseGeocoding']['locations'][-1].get('fullName')
                    location = location.replace(",","|")
                    price = offer['totalPrice'].get('value')

                    # Create a DataFrame with the extracted data
                    offer_df = pd.DataFrame({
                        'OfferID': [offer_id],
                        'Title': [title],
                        'Slug': [slug],
                        'Area': [area],
                        'Rooms': [rooms],
                        'Date': [date],
                        'Location': [location],
                        'Price': [price]
                    })

                    # Append the DataFrame to the list
                    offer_data.append(offer_df)
                except (KeyError, ValueError):
                    print("Json invalid")

            ###break
        
            page_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            today = datetime.today()
            result_day = today.day - page_date.day
            print(f'Page_date: {page_date.day}\n')
            print(f'Result day: {result_day}')

            
            
            if result_day == 0:
                # Increment the page number and run the Spider again
                self.page += 1
                next_page_url = response.url.split('&page=')[0] + f'&page={self.page}'
                yield response.follow(next_page_url, self.parse)
            
            # Concatenate the list of DataFrames into a single DataFrame
            combined_df = pd.concat(offer_data, ignore_index=True)
            
            # Append the DataFrame to the list
            JsonSpider.json_data.append(combined_df)
            
        else:
            self.logger.warning(f'Invalid content type: {content_type}')
    
    def closed(self, reason):
        self.logger.info("Spider closed: %s", reason)
        combine_data()  # Call combine_data when the spider is closed

# After crawling all pages, you can combine the data into a single DataFrame
def combine_data():
    df = pd.concat(JsonSpider.json_data, ignore_index=True)
    df.to_csv('combined_data.csv', index=False)

# You can run the spider and then call combine_data() to combine the data
