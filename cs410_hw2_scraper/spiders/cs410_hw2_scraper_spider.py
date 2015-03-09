__author__ = 'manshu'

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import Request
from scrapy.contrib.spiders import Rule, SitemapSpider, CrawlSpider
from scrapy.contrib.linkextractors import LinkExtractor
from cs410_hw2_scraper.items import Cs410Hw2ScraperItem, PostItem
from stripogram import html2text
import re

class Cs410Hw2ScraperSpider(CrawlSpider):
    name = "cs412_hw2"

    base_url = "https://bbs.archlinux.org/"

    allowed_domains = ["bbs.archlinux.org"]
    start_urls = [
        "https://bbs.archlinux.org",
        # "https://bbs.archlinux.org/viewforum.php?id=35",
        # "https://bbs.archlinux.org/viewtopic.php?id=152930",
        # "https://bbs.archlinux.org/viewtopic.php?id=178747",
        # "https://bbs.archlinux.org/viewtopic.php?id=168828",
    ]

    rules = (
        Rule(LinkExtractor(allow=('viewforum\.php\?id\=', )), callback='parse_forum', follow=True),
        Rule(LinkExtractor(allow=('viewtopic\.php\?id\=', )), callback='parse_topic', follow=True),
        Rule(LinkExtractor(allow=('index\.php', )), callback='parse_main', follow=True)
    )


    def parse_main(self, response):
        self.log("In index page " + response.url)
        items = []

        sel = Selector(response)
        forums = sel.xpath('//div[@class="tclcon"]/div')
        for forum in forums:
            url = forum.xpath('h3/a/@href').extract()[0]
            if not url.startswith(self.base_url) and (url.startswith("http") or url.startswith("www")):
                continue
            item = Cs410Hw2ScraperItem()
            item['name'] = forum.xpath('h3/a/text()').extract()[0]
            #item['desc'] = site.xpath('div[@class="forumdesc"]/text()').extract()#re('-\s[^\n]*\\r')
            if not url.startswith(self.base_url):
                url = self.base_url + url
            item['url'] = url
            items.append(item)
        return items

    def parse_forum(self, response):
        self.log("In forums page " + response.url)

        items = []

        sel = Selector(response)

        topics = sel.xpath('//div[@class="tclcon"]/div')
        for topic in topics:
            url = topic.xpath('a/@href').extract()[0]
            if not url.startswith(self.base_url) and (url.startswith("http") or url.startswith("www")):
                continue
            item = Cs410Hw2ScraperItem()
            item['name'] = topic.xpath('a/text()').extract()[0]
            if not url.startswith(self.base_url):
                url = self.base_url + url
            item['url'] = url
            items.append(item)


        next_forum_page = sel.xpath("//div[@class='linkst']//p[@class='pagelink conl']")[0]
        next_forum_page = next_forum_page.xpath("a[@rel='next']")

        if next_forum_page:
            next_page = next_forum_page[0]
            item = Cs410Hw2ScraperItem()
            item['url'] = self.base_url + next_page.xpath('@href').extract()[0]
            name = sel.xpath("/html/head/title/text()")[0].extract()
            try:
                page = 'Page '
                name = name.replace(',', '')
                page_num = int(name[name.find(page) + len(page):name.find(')')])
                page_num += 1
                name = name.replace(str(page_num - 1), str(page_num))
            except:
                pass
            item['name'] = name
            items.append(item)

        return items

    def parse_topic(self, response):
        self.log("In topics page " + response.url)

        sel = Selector(response)

        title = sel.xpath("//div[@id='brdmain']//ul[@class='crumbs']/li[last()]/strong/a/text()")[0].extract()

        posts = sel.xpath("//div[@id='brdmain']/div[starts-with(@class, 'blockpost')]")

        i = 0
        answers = []
        post_time = ""
        question = ""

        for post in posts:
            time = post.xpath("h2//span/a/text()").extract()[0]
            answer = post.xpath("div[@class='box']//div[@class='postmsg']").extract()[0]
            answer = re.sub(r"[<]cite[>].*?[<][/]cite[>]", "", answer, re.M|re.I)

            answer = html2text(answer)
            answer = answer.replace("\n", " ")
            if i == 0:
                post_time = time
                question = answer
            else:
                answers.append([answer, time])
            i += 1

        post = PostItem()
        post['num_ans'] = i
        post['name'] = title
        post['question'] = question
        post['answers'] = answers
        post['time'] = post_time
        post['url'] = response.url
        post['html'] = response.body
        post['tags'] = []

        #yield post

        next_topic_page = sel.xpath("//div[@class='linkst']//p[@class='pagelink conl']")[0]
        next_topic_page = next_topic_page.xpath("a[@rel='next']")

        item = Cs410Hw2ScraperItem()
        if next_topic_page:
            next_page = next_topic_page[0]
            item['url'] = self.base_url + next_page.xpath('@href').extract()[0]
            name = sel.xpath("/html/head/title/text()")[0].extract()
            try:
                page = 'Page '
                name = name.replace(',', '')
                page_num = int(name[name.find(page) + len(page):name.find(')')])
                page_num += 1
                name = name.replace(str(page_num - 1), str(page_num))
            except:
                pass
            item['name'] = name
            post['name'] = name

        yield post

        if next_topic_page:
            yield item