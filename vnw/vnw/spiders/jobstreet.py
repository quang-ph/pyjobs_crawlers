# -*- coding: utf-8 -*-

import scrapy
from ..keywords import KWS
from ..items import PyjobItem
from ..pymods import xtract, xtract_list, handle_empty_skill
from urllib.parse import urljoin


class TopdevSpider(scrapy.Spider):
    name = "jobstreet"
    allowed_domains = ["jobstreet.vn"]

    start_urls = [
        (urljoin('https://www.jobstreet.vn/vi/job-search/', "job-vacancy.php?ojs=10&key=") + kw) for kw in KWS
    ]

    def parse(self, resp):
        if not resp.xpath('div[@class="position-title header-text"]'
                          '/@href').extract():
            for href in resp.xpath('//div[@class="position-title header-text"]'
                                   '/a/@href').extract():
                yield scrapy.Request(href, self.parse_content)

    def parse_content(self, resp):
        item = PyjobItem()
        item["url"] = resp.url
        item["name"] = xtract_list(resp, '//div[@class="job-position-wrap"]//text()')[0]
        if xtract(resp, '//div[@id="location"]'
                        '/p/span/span[@id="single_work_location"]'):
            item["province"] = xtract(resp, '//div[@id="location"]'
                                            '/p/span/span[@id='
                                            '"single_work_location"]/text()')
        else:
            item["province"] = 'Viet Nam'
        item["wage"] = 'N/A'
        item["post_date"] = xtract(resp, '//p[@id="posting_date"]'
                                         '/span/text()')
        item["company"] = xtract(resp, '//div[@id="company_name"]'
                                       '//text()')
        if xtract(resp, '//div[@id="job_description"]/ul[1]/li'):
            item["work"] = xtract(resp, '//div[@id="job_description"]'
                                        '/ul[1]/li/text()')
        elif xtract(resp, '//div[@id="job_description"]/div/ul[1]/li'):
            item["work"] = xtract(resp, '//div[@id="job_description"]'
                                        '/div/ul[1]/li/text()')
        else:
            item["work"] = xtract(resp, '//div[@id="job_description"]//text()')

        if xtract(resp, '//div[@id="job_description"]/ul[2]/li'):
            item["specialize"] = xtract(resp, '//div[@id="job_description"]'
                                              '/ul[2]/li/text()')
        elif xtract(resp, '//div[@id="job_description"]/div/ul[2]/li'):
            item["specialize"] = xtract(resp, '//div[@id="job_description"]'
                                              '/div/ul[2]/li/text()')
        else:
            item["specialize"] = xtract(resp, '//div[@id="job_description"]'
                                              '/div[2]/text()')

        handle_empty_skill(item)

        yield item
