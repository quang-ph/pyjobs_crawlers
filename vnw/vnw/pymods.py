# -*- coding: utf-8 -*-

import datetime


A_DAY_IN_SEC = 86400


def xtract(response, xpath):
    li = xtract_list(response, xpath)
    return u'|'.join(li)


def xtract_list(response, xpath):
    li = []
    xtracts = response.xpath(xpath).extract()
    for xts in xtracts:
        xts = xts.strip()
        li.append(xts)
    li = filter(None, li)
    return li


def parse_datetime(time):
    '''
    Return datetime string in YYYY-mm-dd format
    '''
    correct_time = str(datetime_from(time)).split(' ')[0]
    return correct_time


def datetime_from(time):
    post_date = str(time)
    post_date = post_date.strip()
    return datetime.datetime.strptime(post_date, '%d-%m-%Y')


def has_expired(time):
    now = datetime.datetime.now()
    return (datetime_from(time) - now).total_seconds() < A_DAY_IN_SEC


def handle_empty_skill(item):
    '''Though the field is required, the site is "free-style" and cannot
    easily determine where this part is, so skip it.
    '''
    if len(item['specialize']) == 0:
        item['specialize'] = 'Xem ở trang gốc'
