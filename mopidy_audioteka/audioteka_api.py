# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

AUDIOTEKA_API_URL = 'https://proxy3.audioteka.com/pl/MobileService.svc/'

DEFAULT_HEADERS = {
    'XMobileAudiotekaVersion': '2.3.15'
}


"""
credentials:

{ 
    'userLogin': user_login, 
    'userPassword': user_password
}

or

{
    'UserLogin': user_login,
    'AuthenticationToken': authentication_token
}

"""


def get_shelf(credentials, session=None, headers=None):
    return _post('get_shelf', credentials, session, {'onlyPaid': 'false'}, headers).json()


def get_shelf_item(product_id, credentials, session=None, headers=None):
    return _post('shelf_item', credentials, session, {'productId': product_id}, headers).json()


def get_chapters(tracking_number, line_item_id, credentials, session=None, headers=None):
    return _post('get_chapters',
                 credentials,
                 session,
                 {'lineItemId': line_item_id, 'LtrackingNumber': tracking_number},
                 headers).json()


def login_get_token(user_login, user_password, session=None, headers=None):
    credentials = {'userLogin': user_login, 'userPassword': user_password}
    return _post('login', credentials, session, {}, headers).json()

#
# >>> print(os.uname())
# ('Linux', 'snowflake', '4.19.12-2-MANJARO', '#1 SMP PREEMPT Sun Dec 23 19:08:00 UTC 2018', 'x86_64')
#

def _post(endpoint, credentials, session=None, data=None, headers=None):
    d, h = _merge_into_data_and_headers(credentials, data, headers if headers else DEFAULT_HEADERS)
    s = session if session else requests.session()
    r = s.post(AUDIOTEKA_API_URL+endpoint, data=d, headers=h)
    r.raise_for_status()
    return r


def _merge_into_data_and_headers(credentials, data, headers):
    ret_data = dict()
    ret_headers = dict()
    ret_data['userLogin'] = credentials['userLogin']
    if 'userPassword' in credentials:
        ret_data['userPassword'] = credentials['userPassword']
    else:
        ret_headers['XMobileTokenAuthentication'] = credentials['AuthenticationToken']
        ret_headers['XMobileUserLogin'] = credentials['userLogin']

    return _merge_dicts(ret_data, data), _merge_dicts(ret_headers, headers)


def _merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result