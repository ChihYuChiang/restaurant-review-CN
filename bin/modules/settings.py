'''
------------------------------------------------------------
General settings
------------------------------------------------------------
'''
CITY_CODE = 'cd' #Target city bj / sh / cd / gz
OUTPUT_PATH = '../data/'
RETRY = 10 #How many times to retry when error in module
LOGPATH_GENERAL = 'log/general'

#Collect review
PAGE_LIMIT = 5 #How many review pages per restaurant to save
REVIEW_THRESHOLD = 200 #Filter for those shops with reviews more than the threshold

#Get url
ZONELIST_FILE = 'dianping_zone.csv'
ZONE_PREFIX = ''








'''
------------------------------------------------------------
Browser
------------------------------------------------------------
'''
DOWNLOAD_TIMEOUT = 20 #Second
LOGPATH_PHANTOM = 'log/ghostdriver.log'
USERAGENT_CANDIDATES = [#Acquire updated user agents from: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
]
HEADER_COOKIE = r'cy=2335; cye=taipei; _lxsdk_cuid=160b8a2149bc8-0e0b52e0643b88-b7a103e-384000-160b8a2149cc8; _lxsdk=160b8a2149bc8-0e0b52e0643b88-b7a103e-384000-160b8a2149cc8; _hc.v=a096c605-9bda-81c1-3c90-05535ede0dd6.1514926119; s_ViewType=10; __mta=155557764.1514926135086.1514926135086.1514926135086.1; __utma=1.892976347.1514935641.1514935641.1514935641.1; __utmc=1; __utmz=1.1514935641.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _lxsdk_s=160c4764d49-a-c00-a2b%7C%7C0'

#(Currently unused)
SERVICE_ARGS = [#Can be added to webdriver.PhantomJS(service_args)
    '--proxy=127.0.0.1:9999',
    '--proxy-type=http',
    '--ignore-ssl-errors=true'
]