import logging
import requests
import string

from scrapy.conf import settings
from scrapy.exceptions import DropItem

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


class ValidatePipeline(object):
    def process_item(self, item, spider):
        if not item:
            logger.error('Drop job, item is empty')
            raise DropItem
        try:
            kv = {kw: item[kw] for kw in REQUIRED_FIELDS}
        except KeyError as e:
            logger.error('Drop job: {} {}, missing required key {}'.format(
                            item.get('name', 'MISSING'),
                            item.get('url', 'MISSING'),
                            e)
                         )
            raise DropItem
        for k, v in kv.iteritems():
            assert isinstance(v, str), (
                    "Pipeline only accepts string, "
                    "crawler must preprocess other types to string")
            if v.strip().strip(string.punctuation) == '':
                logger.error('Drop job: {} {}, required key {} is empty'.format(
                                item.get('name', 'MISSING'),
                                item.get('url', 'MISSING'),
                                k)
                             )
                raise DropItem

        item = xtract_item(item)
        return item


class APIPipeline(object):
    collection_name = 'scrapy_items'

    def __init__(self):
        self.url = 'http://127.0.0.1:5000/python'

    def process_item(self, item, spider):
        # Dropped item in prior step in pipeline
        if item is None:
            raise DropItem
        try:
            resp = requests.post(self.url, json=item._values)
            if resp.status_code == 200:
                logger.info('Added job {}, response {}'.format(
                            item._values.get('url'), resp.content))
                item.update({"created": resp.json()['created']})
                return item
            else:
                logger.error('Failed adding job {}, response {}'.format(
                             item._values.get('url'), resp.content))
                raise DropItem
        except KeyError as e:
            logger.error('Error when posting: {}'.format(e))
            raise DropItem


class FBPagePipeline(object):
    def process_item(self, item, spider):
        send(item)


FBAPI = 'https://graph.facebook.com/v2.10/'
PJ_PAGE_ID = '187862604923059'

PAGEPOST = FBAPI + PJ_PAGE_ID + "/feed"


def send(item):
    page_token = settings.get('FB_PAGE_ACCESS_TOKEN')

    if len(page_token) > 0:
        logger.debug("Token is not empty")

    params = {'access_token': page_token}

    payload = {"message": item._values.get('name'), "link": item._values.get('created')}

    logger.info("About to send {}".format(payload))

    params.update(payload)
    r = requests.post(PAGEPOST, params=params)
    if r.status_code == 200:
        logger.info(r, r.text)
    else:
        logger.error("Failed to send to FB page. Response {} {}".format(r, r.text))
        raise DropItem
