import os

ITVIEC_USERNAME = ''
ITVIEC_PASSWORD = ''

BOT_NAME = 'vnw'

SPIDER_MODULES = ['vnw.spiders']
NEWSPIDER_MODULE = 'vnw.spiders'
ITEM_PIPELINES = {
    'vnw.pipelines.TextFilePipeline': 500,
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = 'False'

USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')

is_prod = os.environ.get('PYJOBS_IS_PROD', False)
if is_prod:
    DOWNLOAD_DELAY = 2
    DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # NOQA
        'vnw.rotate_useragent.RotateUserAgentMiddleware': 400
    }

    try:
        import prodsettings as prod
    except ImportError:
        pass
    else:
        VIETNAMWORK_USERNAME = prod.custom.get('VIETNAMWORK_USERNAME', 'some_username')
        VIETNAMWORK_PASSWORD = prod.custom.get('VIETNAMWORK_PASSWORD', 'some_password')
        ITVIEC_USERNAME = prod.custom.get('ITVIEC_USERNAME', '')
        ITVIEC_PASSWORD = prod.custom.get('ITVIEC_PASSWORD', '')
        FB_PAGE_ACCESS_TOKEN = prod.custom.get('fb_page_access_token', '')
