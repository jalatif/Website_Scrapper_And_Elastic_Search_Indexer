# -*- coding: utf-8 -*-

# Scrapy settings for cs410_hw2_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'cs410_hw2_scraper'

SPIDER_MODULES = ['cs410_hw2_scraper.spiders']
NEWSPIDER_MODULE = 'cs410_hw2_scraper.spiders'

DEFAULT_ITEM_CLASS = 'cs410_hw2_scraper.items.Cs410Hw2ScraperItem'

ITEM_PIPELINES = {'cs410_hw2_scraper.pipelines.FilterUrlsPipeline': 1,
                  'cs410_hw2_scraper.pipelines.DuplicateUrlsPipeline': 2}

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 0.5

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cs410_hw2_scraper (+http://www.yourdomain.com)'
