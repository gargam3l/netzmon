from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from netzmon.sources import connectivity_check
from .spiders.modem_status_spider import ModemStatusSpider
from netzmon.sources import config


def run_crawl():
    """
    Run a spider within Twisted. Once it completes,
    wait 5 seconds and run another spider.
    """
    process = CrawlerProcess(get_project_settings())
    process.crawl(ModemStatusSpider)
    process.start()
    # you can use reactor.callLater or task.deferLater to schedule a function
    # deferred.addCallback(reactor.callLater, 5, run_crawl)
    # return deferred


def main():
    config.setup_logging()
    connectivity_check.generate_connectivity_test()
    run_crawl()
# TODO Add upload to AWS S3


if __name__ == '__main__':
    main()
