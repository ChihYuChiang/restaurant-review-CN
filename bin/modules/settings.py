CITY_CODE = 'gz' #Target city bj / sh / cd / gz
OUTPUT_PATH = '../data/'
RETRY = 5 #How many times to retry when error in module
PAGE_LIMIT = 5 #How many review pages per restaurant to save
REVIEW_THRESHOLD = 200 #Filter for those shops with reviews more than the threshold
ZONELIST_FILE = 'dianping_zone.csv'
ZONE_PREFIX = ''

#--Acquire updated user agents from: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
USERAGENT_CANDIDATES = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38'
]
HEADER_COOKIE = 'PHOENIX_ID=0a010725-15e38404ab2-e498b4e; _hc.v=c9678f60-ffb1-70f3-6cc2-ca97c011b225.1492122470; __mta=43235098.1504182293440.1504182293440.1506927949288.2; _lxsdk=15e383e817439-0148d385f6254f-e313761-384000-15e383e8175c8;_lxsdk_cuid=15e383e817439-0148d385f6254f-e313761-384000-15e383e8175c8;aburl=1; cy=2; cye=beijing; s_ViewType=10'