import scrapy


class ReviewSpider(scrapy.Spider):
    name = "review"

    def start_requests(self):
        urls = [
            'http://www.dreamsyssoft.com/python-scripting-tutorial/shell-tutorial.php'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split(r'/')[-2]
        filename = 'review-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
