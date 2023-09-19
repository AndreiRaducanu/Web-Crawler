from storia.spiders.get_token import TokenSpider
from storia.spiders.get_json import JsonSpider
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings




"""class RunSpiders:
    def __init__(self):
        self.process = CrawlerProcess()
        self.token = None
        self.json_data = None
        self.build_id = None

    def get_token_and_json(self, page_number):
        self.process.crawl(TokenSpider)
        #self.process.crawl(JsonSpider)  # Add TokenSpider and JsonSpider to the same process
        self.process.start()  # Start the process once
        build_id = TokenSpider.build_id

        if build_id is not None:
            self.build_id = build_id
            self.process.crawl(JsonSpider, page=page_number, token=self.build_id)
        else:
            raise ValueError("Unable to get token")

    

        # You can add a callback function here to handle the JSON data when it's ready

spider_runner = RunSpiders()
spider_runner.get_token_and_json(5)


class MySpider1(scrapy.Spider):
    # Your first spider definition
    ...


class MySpider2(scrapy.Spider):
    # Your second spider definition
    ...
"""

settings = get_project_settings()
configure_logging(settings)
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(TokenSpider)
    yield runner.crawl(JsonSpider, page=4, token=TokenSpider.build_id)
    reactor.stop()


crawl()
reactor.run()