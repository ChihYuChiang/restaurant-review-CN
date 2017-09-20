import scrapy


class ReviewSpider(scrapy.Spider):
    name = "review"

    def start_requests(self):
        urls = [
            'http://webcache.googleusercontent.com/search?q=cache:http://www.dianping.com/shop/6088238/review_more%3Fpageno%3D1&num=1&strip=1&vwsrc=0',
            'http://webcache.googleusercontent.com/search?q=cache:http://www.dianping.com/shop/6088238/review_all%3Fpageno%3D2&num=1&strip=1&vwsrc=0',
            'http://webcache.googleusercontent.com/search?q=cache:http://www.dianping.com/shop/6088238/review_all%3Fpageno%3D3&num=1&strip=1&vwsrc=0',
            'http://webcache.googleusercontent.com/search?q=cache:http://www.dianping.com/shop/6088238/review_all%3Fpageno%3D4&num=1&strip=1&vwsrc=0',
            'http://webcache.googleusercontent.com/search?q=cache:http://www.dianping.com/shop/6088238/review_all%3Fpageno%3D5&num=1&strip=1&vwsrc=0'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split('=')[2].strip('&strip')
        filename = 'review-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
