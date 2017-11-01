import scrapy
import pandas as pd
from modules import utils

class ReviewSpider(scrapy.Spider):
    name = "main"
    items = utils.sourceItem(REVIEW_THRESHOLD)
    shopIds_problematic = utils.problematicResult(targetList=items.shopId, targetPath='../data/raw/main/')

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
