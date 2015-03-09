__author__ = 'manshu'

__author__ = 'manshu'

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import Request
from scrapy.contrib.spiders import Rule, SitemapSpider, CrawlSpider
from scrapy.contrib.linkextractors import LinkExtractor
from cs410_hw2_scraper.items import Cs410Hw2ScraperItem, PostItem
from stripogram import html2text
import re

class StackOverflowSpider(CrawlSpider):
    name = "stack_overflow"

    base_url = "https://stackoverflow.com"
    sort_by_vote = "?answertab=votes#tab-top"

    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/questions?page=1&sort=votes",
        #"http://stackoverflow.com/questions/1554099/why-is-the-android-emulator-so-slow-how-we-can-speed-up-the-android-emulator" + sort_by_vote,
    ]

    rules = (
        Rule(LinkExtractor(allow=('questions\/[0-9]+/[a-zA-Z-_]+', )), callback='parse_answers', follow=True),
        Rule(LinkExtractor(allow=('questions$', )), callback='parse_questions', follow=True),
    )

    def parse_questions(self, response):
        self.log("In questions page " + response.url)
        items = []

        sel = Selector(response)
        questions_this_page = sel.xpath("//div[@class='question-summary']")

        page_questions = []
        for question_summary in questions_this_page:

            question_votes = question_summary.xpath("div[@class='statscontainer']//div[@class='votes']//strong/text()")
            question_answers = question_summary.xpath("div[@class='statscontainer']/div[@class='stats']/div[contains(@class, 'status')]/strong/text()").extract()[0]

            question = question_summary.xpath("div[@class='summary']")
            url_question = self.base_url + question.xpath("h3/a/@href").extract()[0] + self.sort_by_vote
            question_title = question.xpath("h3/a/text()").extract()[0]
            question_tags = question.xpath("div[contains(@class, 'tag')]//a/text()").extract()
            item = Cs410Hw2ScraperItem()
            item['url'] = url_question
            item['name'] = question_title
            page_questions.append(item)

        try:
            url = response.url
            page_num = int(url[url.find("page=") + 5])
            url = url.replace("page=" + str(x), "page=" + str(x + 1))
            item = Cs410Hw2ScraperItem()
            item['url'] = url
            item['name'] = sel.xpath("/html/head/title/text()").extract()[0]
            page_questions.append(item)
        except:
            pass

        return page_questions

    def parse_answers(self, response):
        self.log("In answers page " + response.url)
        items = []

        sel = Selector(response)

        try:
            question_title = sel.xpath("//div[@id='question-header']//a/text()").extract()[0]

            question_url = self.base_url + sel.xpath("//div[@id='question-header']//a/@href").extract()[0]

            question = sel.xpath("//div[@id='mainbar']/div[@class='question'][@id='question']")
            post_time = question.xpath("table//div[@class='user-action-time']//span[@class='relativetime']/@title").extract()[0]
            answers = sel.xpath("//div[@id='mainbar']/div[@id='answers']/div[contains(@class, 'answer')]")

            question_text = question.xpath("//td[@class='postcell']//div[@class='post-text']").extract()[0]
            question_tags = question.xpath("//td[@class='postcell']//div[@class='post-taglist']//a/text()").extract()

            question_text = html2text(question_text)
            question_text = question_text.replace("\n", " ")
        except:
            pass
        question_answers = []
        for ans in answers:
            try:
                answer = ans.xpath("table//div[@class='post-text']").extract()[0]
                posted_time = ans.xpath("table//div[@class='user-action-time']//span[@class='relativetime']/@title").extract()[0]
                answer = html2text(answer)
                answer = answer.replace("\n", " ")
                question_answers.append([answer, posted_time])
            except:
                pass


        post = PostItem()
        post['num_ans'] = len(question_answers)
        post['name'] = question_title
        post['question'] = question_text
        post['answers'] = question_answers
        post['time'] = post_time
        post['url'] = question_url
        post['html'] = response.body
        post['tags'] = question_tags

        yield post