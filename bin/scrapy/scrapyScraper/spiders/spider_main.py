import scrapy
import pandas as pd


class ReviewSpider(scrapy.Spider):
    name = "main"

    def start_requests(self):
        urls = [
            'http://www.dianping.com/shop/5568696',
            'http://www.dianping.com/shop/6088238'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        shopId = response.url.strip('http://www.dianping.com/shop/')
        filename = '%s.html' % shopId
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
