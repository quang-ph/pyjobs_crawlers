# -*- coding: utf-8 -*-
import time

import scrapy
import logging

from selenium import webdriver
from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.settings import Settings
from selenium.webdriver import ActionChains

from ..items import companyItem
from ..pymods import xtract

from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger()

settings = Settings()


class VnwCompanySpider(InitSpider):
    name = "vnw-company"
    allowed_domains = ["vietnamworks.com"]
    login_page = "http://www.vietnamworks.com/login"
    start_urls = [
        # "https://www.vietnamworks.com/job-search/all-jobs",
        "https://www.vietnamworks.com/tim-viec-lam/tat-ca-viec-lam"
    ]
    unique_data = set()

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
        page = 1
        while True:
            print(f'Page {page}')
            html = self.driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            time.sleep(3)
            for div in self.driver.find_elements_by_xpath(
                    '//div[@class="job-item animated fadeIn position-relative job-priority"]'):
                url_tag = div.find_element_by_class_name("job-title")
                url = url_tag.get_attribute("href")
                request = scrapy.Request(url, self.parse_content, dont_filter=True)
                request.meta["keyword"] = keyword
                yield request
            element = self.driver.find_element_by_xpath('//*[@class="page-item"][last()-1]/a')
            if element.text == ">":
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()
                element.click()
                page += 1
            else:
                break
        self.driver.close()

    def parse_content(self, resp):
        item = companyItem()
        item["name"] = xtract(resp, '//div[@class="col-sm-12 company-name"]/a/text()').split("|")[0]
        item["address"] = xtract(resp, '//*[@id="company-info"]/div/div[2]/div/div/div[1]/div[2]/span[2]/text()')
        item["size"] = xtract(resp, '//*[@id="company-info"]/div/div[2]/div/div/div[2]/div[2]/span[2]/text()')
        item["logo"] = xtract(resp, '//*[@id="wrapper"]/div[3]/div[5]/section[1]/div/div[2]/div[1]/span/a/img/@src')
        if item["logo"] == '':
            item["logo"] = xtract(resp,
                                  '//*[@id="wrapper"]/div[3]/div[4]/div[1]/section/div/div[2]/div[1]/span/a/img/@src')
        print(f"Parsed 1 item: {item}")
        if item["name"] not in self.unique_data:
            self.unique_data.add(item["name"])
            yield item
        else:
            print(f"Duplicated ----------- {item['name']}")
