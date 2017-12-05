import scrapy
import pandas as pd
import os, sys

#Import customized modules
#binpath is the path /bin
binPath = os.path.split(os.getcwd())[0]
sys.path.insert(0, binPath)
from modules import utils as c_utils
from modules import settings as c_settings


class MainSpider(scrapy.Spider):
    #Class main for command line calls
    name = "main"

    #Initiate target items (problematic shops)
    def __init__(self):
        self.items = c_utils.sourceItem(binPath + '/' + c_settings.OUTPUT_PATH, c_settings.REVIEW_THRESHOLD, c_settings.CITY_CODE)
        self.shopIds_problematic = c_utils.problematicResult(targetList=self.items.shopId, targetPath=os.path.split(binPath)[0] + '/data/raw_{}/main/'.format(c_settings.CITY_CODE))
        self.log('Number of target files = ' + str(len(self.shopIds_problematic)))


    def start_requests(self):
        urls = ('http://www.dianping.com/shop/' + shopId for shopId in self.shopIds_problematic[0:100]) #Limit number of target per time/day (could be blocked if go over that)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        shopId = response.url.strip('http://www.dianping.com/shop/')
        filename = os.path.split(binPath)[0] + '/data/raw_{}/main/'.format(c_settings.CITY_CODE) + '%s.html' % shopId
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
