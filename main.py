from storia.spiders.get_token import TokenSpider
from storia.spiders.get_json import JsonSpider
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
import time
import discord
from credentials import TOKEN, CHANNEL_ID

# Set up Scrapy settings
settings = {
    'USER_AGENT': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    ),
    'LOG_ENABLED': False,  # Disable Scrapy logs if needed
    # Add other settings as required
}


configure_logging(settings)

# Initialize the CrawlerRunner with the settings
runner = CrawlerRunner(settings)

# Initialize the list to store offer IDs
old_id = []


@defer.inlineCallbacks
def crawl():
    retries = 5  # Number of times to run both spiders
    while retries > 0:
        try:
            yield runner.crawl(TokenSpider)
            yield runner.crawl(
                JsonSpider,
                page=7,
                token=TokenSpider.build_id
            )  # page represents start page
            new_id = JsonSpider.offer_ids

            # Check for new IDs
            new_offers = set(new_id) - set(old_id)
            if new_offers:
                old_id.extend(new_offers)
                print(f'Appended new offers: {new_offers}')
                # post_message(list(new_offers))
                post_message([1, 2, 3])

            # Delay between runs
            time.sleep(300)

        finally:
            retries -= 1  # Decrement the retry counter

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
    crawl()  # Start the crawling process

    # Start the Twisted reactor
    reactor.run()
