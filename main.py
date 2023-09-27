import time
import threading
import discord
from gevent.pywsgi import WSGIServer
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from crawler.spiders.get_token import TokenSpider
from crawler.spiders.get_json import JsonSpider
from credentials import TOKEN, CHANNEL_ID
from web.app import app
from typing import List

# Set up Scrapy settings
settings = {
    'USER_AGENT': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '  # noqa E501
                   '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'),
    'LOG_ENABLED': False,  # Disable Scrapy logs
}

configure_logging(settings)

# Initialize the CrawlerRunner with the settings
runner = CrawlerRunner(settings)

# List to store offer IDs
old_id: List[int] = []


def start_flask_app():
    # Create a Gevent WSGI server to serve the Flask app
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()


@defer.inlineCallbacks
def crawl():
    retries = 5  # Number of times to run both spiders
    while retries > 0:
        try:
            # Run Scrapy spiders
            yield runner.crawl(TokenSpider)
            yield runner.crawl(JsonSpider, page=7, token=TokenSpider.build_id)
            new_id = JsonSpider.offer_ids

            # Check for new IDs
            new_offers = set(new_id) - set(old_id)
            if new_offers:
                old_id.extend(new_offers)
                print(f'Appended new offers: {new_offers}')
                # post_message(list(new_offers))

        finally:
            retries -= 1  # Decrement the retry counter
        time.sleep(3)  # Delay between runs

    # Stop the reactor when all spiders are done
    reactor.stop()


def post_message(msg_list):
    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        print('Logged in')
        channel = client.get_channel(CHANNEL_ID)
        for url in msg_list:
            await channel.send(url)
        await client.close()

    client.run(TOKEN)


if __name__ == "__main__":
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    # Start the crawling process
    crawl()
    reactor.run()
    flask_thread.join()
