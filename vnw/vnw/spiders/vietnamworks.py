# -*- coding: utf-8 -*-

import scrapy
import dateutil.parser
import logging

from selenium import webdriver
from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.settings import Settings

from ..items import PyjobItem
from ..pymods import xtract
from ..keywords import KWS

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger()

settings = Settings()


class VnwSpider(InitSpider):
    name = "vietnamworks"
    allowed_domains = ["vietnamworks.com"]
    login_page = "http://www.vietnamworks.com/login"
    start_urls = [
        ("http://www.vietnamworks.com/" + kw + "-kw") for kw in KWS
    ]

    def __init__(self):
        self.driver = webdriver.Chrome()

    def init_request(self):
        return Request(url=self.login_page, callback=self.login)

    def login(self, resp):
        user = settings.get(name='VIETNAMWORK_USERNAME')
        password = settings.get(name='VIETNAMWORK_PASSWORD')
        return FormRequest.from_response(resp,
                                         method='POST',
                                         formdata={'form[username]': user,
                                                   'form[password]': password},
                                         callback=self.check_login,
                                         dont_filter=True
                                         )

    def check_login(self, resp):
        return self.initialized()

    def parse(self, resp):
        print(f'Begin parse {resp}')
        url = resp.url
        keyword = url.split('.com/')[1].split('-kw')[0]
        self.driver.get(url)
        for div in self.driver.find_elements_by_xpath('//div[@class="job-item animated fadeIn position-relative job-priority"]'):
            try:
                posted = div.find_element_by_class_name("posted-date")
            except Exception as e:
                print(e)
                _logger.info(str(e))
                break
            post_date = posted.text.split(': ')[1]
            if post_date.lower() == 'today':
                convert_post_date = dateutil.parser.datetime.datetime.now().date()
            else:
                convert_post_date = dateutil.parser.parse(post_date)
            url_tag = div.find_element_by_class_name("job-title")
            url = url_tag.get_attribute("href")
            request = scrapy.Request(url, self.parse_content, dont_filter=True)
            request.meta["keyword"] = keyword
            request.meta["post_date"] = str(convert_post_date).split(' ')[0]
            yield request
        self.driver.close()

    def parse_content(self, resp):
        item = PyjobItem()
        item["url"] = resp.url
        item["keyword"] = resp.meta["keyword"]
        item["post_date"] = resp.meta["post_date"]
        item["name"] = xtract(resp, '//h1[@itemprop="title"]/text()')
        item["company"] = xtract(resp,
                                 '//span[@class="company-name text-lg block"]'
                                 '/strong/text()')
        item["address"] = xtract(resp, '//span[@class="company-address block"]'
                                       '/text()')
        item["province"] = xtract(resp, '//span[@itemprop="address"]/a/text()')
        item["wage"] = xtract(resp, '//span[@class="orange '
                                    'bold-700 text-lg"]/text()')
        item["work"] = xtract(resp, '//div[@id="job-description"]/text()')
        item["specialize"] = xtract(resp, '//div[@class=""]/text()')
        item["information"] = xtract(resp,
                                     '//span[@id="companyprofile"]/text()')
        try:
            item["contact"] = resp.xpath('//div[@class="company-info"]/p/strong/'
                                         'text()').extract()[0].strip()
        except IndexError:
            item["contact"] = ''
        try:
            item["size"] = resp.xpath('//div[@class="company-info"]/p/strong/'
                                      'text()').extract()[1].strip()
        except IndexError:
            item["size"] = ''
        item["logo"] = xtract(resp, '//img[@class="logo img-responsive"]/@src')
        item["expiry_date"] = ''
        print(f"Parsed 1 item:  {item}")
        yield item
