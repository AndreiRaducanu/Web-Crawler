import scrapy
from datetime import datetime
import pandas as pd
import os
from typing import List, Dict, Any, Set


class JsonSpider(scrapy.Spider):
    name = 'json_spider'
    json_data: List[Dict[str, Any]] = []
    offer_ids: Set[int] = set()

    def __init__(self, page, token):
        self.page = int(page)
        self.token = token
        self.base_url = (
            f'https://www.storia.ro/_next/data/{self.token}/'
            'ro/rezultate/inchiriere/apartament/bucuresti.json'
        )

    custom_query = {
        "market": "ALL",
        "ownerTypeSingleSelect": "ALL",
        "distanceRadius": "0",
        "viewType": "listing",
        "searchingCriteria": ["inchiriere", "apartament", "bucuresti"]
    }

    custom_settings = {
        'USER_AGENT': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        )
    }

    def start_requests(self):
        self.custom_query['page'] = str(self.page)
        query_parts = [f'{key}={value}' for key, value in self.custom_query.items()]
        query_string = '&'.join(query_parts)
        url = f'{self.base_url}?{query_string}'
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        content_type = (
            response.headers.get('Content-Type', b'')
            .decode('utf-8')
            .lower()
        )

        if 'application/json' in content_type:
            json_data = response.json()
            items_data = json_data['pageProps']['data']['searchAds']['items']
            items_page = len(items_data)
            print(f'Items in page: {str(items_page)}')

            offer_data = []

            for offer in json_data['pageProps']['data']['searchAds']['items']:
                try:
                    offer_id, title, slug, area, rooms, date, location, price, currency = \
                    self.extract_offer_data(offer)

                    offer_df = pd.DataFrame({
                        'OfferID': [offer_id],
                        'Title': [title],
                        'Link': [slug],
                        'Area': [area],
                        'Rooms': [rooms],
                        'Date': [date],
                        'Location': [location],
                        'Price': [price],
                        'Currency': [currency]
                    })

                    offer_data.append(offer_df)
                    JsonSpider.offer_ids.add(offer_id)
                except (KeyError, ValueError):
                    print("Invalid JSON")

            if self.should_continue_crawling(json_data):
                next_page_url = self.get_next_page_url(response.url)
                yield response.follow(next_page_url, self.parse)

            combined_df = pd.concat(offer_data, ignore_index=True)
            JsonSpider.json_data.append(combined_df)

        else:
            self.logger.warning(f'Invalid content type: {content_type}')

    def extract_offer_data(self, offer):
        offer_id = offer['id']
        title = offer['title']
        slug = 'https://www.storia.ro/ro/oferta/' + offer['slug']
        area = offer['areaInSquareMeters']
        rooms = offer['roomsNumber']
        date = offer['dateCreated']
        location = self.extract_location(offer)
        price, currency = self.extract_price_and_currency(offer)

        return offer_id, title, slug, area, rooms, date, location, price, currency

    def extract_location(self, offer):
        loc_path = offer['location']['reverseGeocoding']['locations'][-1]
        location = loc_path.get('fullName')
        location = location.replace(",", "|")
        return location

    def extract_price_and_currency(self, offer):
        price = offer['totalPrice'].get('value')
        currency = offer['totalPrice'].get('currency')

        if currency != "EUR":
            currency = int(price) // 5
            currency = "EUR"

        return price, currency

    def should_continue_crawling(self, json_data):
        page_path = json_data['pageProps']['data']['searchAds']['items'][0]['dateCreated']
        page_date = datetime.strptime(page_path, '%Y-%m-%d %H:%M:%S')
        today = datetime.today()
        result_day = today.day - page_date.day
        print(f'Page_date: {page_date.day}\n')
        print(f'Result day: {result_day}')
        return result_day == 0

    def get_next_page_url(self, current_url):
        return current_url.split('&page=')[0] + f'&page={self.page + 1}'

    def closed(self, reason):
        self.logger.info("Spider closed: %s", reason)
        self.combine_data()

    def combine_data(self):
        # Define the path to the 'src' folder
        src_folder = os.path.join(os.path.dirname("Web-Crawler"))
        test_txt_path = os.path.join(src_folder, 'combined_data.csv')
        df = pd.concat(JsonSpider.json_data, ignore_index=True)
        df.to_csv(test_txt_path, index=False)
