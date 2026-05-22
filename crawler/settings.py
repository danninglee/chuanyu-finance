BOT_NAME = "chuanyu_finance"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 2.0
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

DOWNLOADER_MIDDLEWARES = {
    "crawler.middleware.RandomUserAgentMiddleware": 543,
}

ITEM_PIPELINES = {
    "crawler.pipeline.PostgresPipeline": 300,
}

LOG_LEVEL = "INFO"
