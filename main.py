from storia.spiders.get_token import TokenSpider
from storia.spiders.get_json import JsonSpider
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import time

# Set up Scrapy settings
settings = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'LOG_ENABLED': False,  # Disable Scrapy logs if needed
    # Add other settings as required
}

configure_logging(settings)

# Initialize the CrawlerRunner with the settings
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    retries = 5  # Number of times to run both spiders
    while retries > 0:
        try:
            yield runner.crawl(TokenSpider)
            yield runner.crawl(JsonSpider, page=7, token=TokenSpider.build_id)  # page represents start page
            if True:
                pass  # send discord message with the offer
            
        finally:
            retries -= 1  # Decrement the retry counter

    # Stop the reactor when all spiders are done
    reactor.stop()

crawl()  # Start the crawling process

# Start the Twisted reactor
reactor.run()

print("Offer IDs:", JsonSpider.offer_ids)

while True:
    time.sleep(30)
    # Start crawling process
    # Store the IDs
    # Start crawling process again
    # Check for new IDs
    # If new ID found, add it to the current list and send Discord notification
