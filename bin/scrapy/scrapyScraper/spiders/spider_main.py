import scrapy
import pandas as pd
import os, sys

#Import customized modules
binPath = os.path.split(os.getcwd())[0]
sys.path.insert(0, binPath)
from modules import utils as c_utils
from modules import settings as c_settings


class ReviewSpider(scrapy.Spider):
    name = "main"
    items = c_utils.sourceItem(binPath + '/' + c_settings.OUTPUT_PATH, c_settings.REVIEW_THRESHOLD)
    shopIds_problematic = c_utils.problematicResult(targetList=items.shopId, targetPath=os.path.split(binPath)[0] + '/data/raw/main/')


    def start_requests(self):
        urls = ('http://www.dianping.com/shop/' + shopId for shopId in self.shopIds_problematic)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        shopId = response.url.strip('http://www.dianping.com/shop/')
        filename = os.path.split(binPath)[0] + '/data/raw/main/' + '%s.html' % shopId
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
