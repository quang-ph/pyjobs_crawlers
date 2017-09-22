import logging
import requests
import string

from scrapy.conf import settings

logger = logging.getLogger(__name__)
REQUIRED_FIELDS = ['company', 'name', 'province', 'url', 'work', 'specialize']


def xtract_item(item):
    for key, value in item.iteritems():
        value = value.strip().strip('-+:')
        item[key] = value
    return item


class VnwPipeline(object):
    def process_item(self, item, spider):
        return item


# http://stackoverflow.com/questions/13527921/scrapy-silently-drop-an-item
# Return None to drop item and avoid annoying warning log when drop
class ValidatePipeline(object):
    def process_item(self, item, spider):
        if not item:
            logger.error('Drop job, item is empty')
            return None
        try:
            kv = {kw: item[kw] for kw in REQUIRED_FIELDS}
        except KeyError as e:
            logger.error('Drop job: %s %s, missing required key %r',
                         item.get('name', 'MISSING'),
                         item.get('url', 'MISSING'),
                         e)
            return None
        for k, v in kv.iteritems():
            assert isinstance(v, basestring), (
                    "Pipeline only accepts string, "
                    "crawler must preprocess other types to string")
            if v.strip().strip(string.punctuation) == '':
                logger.error('Drop job: %s %s, required key %r is empty',
                             item.get('name', 'MISSING'),
                             item.get('url', 'MISSING'),
                             k)
                return None

        item = xtract_item(item)
        return item


class APIPipeline(object):
    collection_name = 'scrapy_items'

    def __init__(self):
        self.url = 'http://127.0.0.1:5000/python'

    def process_item(self, item, spider):
        # Dropped item in prior step in pipeline
        if item is None:
            return
        try:
            resp = requests.post(self.url, json=item._values)
            if resp.status_code == 200:
                logger.info('Added job %s, response %s',
                            item._values.get('url'), resp.content)
                return item
            else:
                logger.error('Failed adding job %s, response %s',
                             item._values.get('url'), resp.content)
        except KeyError as e:
            logger.error('Error when posting: %s', e)


class FBPagePipeline(object):
    def process_item(self, item, spider):
        send(item)


def send(item):
    API = 'https://graph.facebook.com/v2.10/'
    # THIS current use genearted page token
    page_token = settings.get('fb_page_access_token')
    params = {'access_token': page_token}  # NOQA

    page = 'pyjobsvn?fields=access_token'

    job = item
    payload = {"message": job['title'], "link": job['link']}

    pageid = requests.get(API + page, params=params).json()['id']
    post_endpoint = pageid + "/feed"
    params.update(payload)
    r = requests.post(API + post_endpoint, params=params)
    if r.status_code == 200:
        print(r, r.text)
    else:
        logger.error("Failed to send to FB page. Response %s %r", r, r.text)
