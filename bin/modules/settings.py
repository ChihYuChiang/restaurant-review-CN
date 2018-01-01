CITY_CODE = 'gz' #Target city bj / sh / cd / gz
OUTPUT_PATH = '../data/'
RETRY = 5 #How many times to retry when error in module
DOWNLOAD_TIMEOUT = 20 #Second
PAGE_LIMIT = 5 #How many review pages per restaurant to save
REVIEW_THRESHOLD = 200 #Filter for those shops with reviews more than the threshold
ZONELIST_FILE = 'dianping_zone.csv'
ZONE_PREFIX = ''

#--Acquire updated user agents from: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
USERAGENT_CANDIDATES = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
]
HEADER_COOKIE = r' _hc.v=c9678f60-ffb1-70f3-6cc2-ca97c011b225.1492122470; __mta=43235098.1504182293440.1504182293440.1506927949288.2; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; _lxsdk=15e383e817439-0148d385f6254f-e313761-384000-15e383e8175c8; _lxsdk_s=160b0fa9256-987-757-0b%7C%7C12; _lxsdk_cuid=15e383e817439-0148d385f6254f-e313761-384000-15e383e8175c8;aburl=1; cy=2; cye=beijing; s_ViewType=10;aburl=1; cy=18; cye=shenyang; s_ViewType=10; _hc.s="\"c9678f60-ffb1-70f3-6cc2-ca97c011b225.1492122470.1513733635.1513733652\""; m_rs=af2fda47-6dbd-40bc-992e-2bd8afae8ace'