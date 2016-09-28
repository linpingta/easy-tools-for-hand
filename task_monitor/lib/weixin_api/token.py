import os
import requests
import time
import simplejson as json
from store import WeixinTokenStorage, WeixinTokenFileStorage


class WeixinToken(object):
    ''' Weixin token' storage and update
    '''
    @classmethod
    def init(cls, app_id=None, app_secret=None, storage=None, weixin_url='', qiye_flag=True, node='gettoken', grant_type='client_credential'):
	cls.app_id = app_id
	cls.app_secret = app_secret
	cls.WEIXIN_URL = weixin_url
	cls.qiye_flag = qiye_flag
	app_to_token_dict = storage.get_app_to_token_dict()
	if app_to_token_dict:
	    cls.access_token = app_to_token_dict[app_id]['access_token']
	else:
	    cls.access_token = -1
	cls.grant_type = grant_type
	cls.node = node
	cls.storage = storage

    @classmethod
    def _access_token_valid(cls, logger):
	''' check whther access_token still valid'''
	access_token_valid = False
	try:
	    unix_now = int(time.mktime(time.localtime()))
	    app_to_token_dict = cls.storage.get_app_to_token_dict()
	    
	    if (not app_to_token_dict) or (cls.app_id not in app_to_token_dict):
		logger.warning('app_to_token_dict not valid with app_id %s' % cls.app_id)
	    else:
		fetch_unix_time = app_to_token_dict[cls.app_id]['fetch_unix_time']
		expires_in = app_to_token_dict[cls.app_id]['expires_in']
		access_token_valid = unix_now - fetch_unix_time < expires_in
	except Exception as e:
	    logger.exception(e)
	    return False
	else:
	    return access_token_valid

    @classmethod
    def update_access_token(cls, logger):
	try:
	    unix_now = int(time.mktime(time.localtime()))

	    # call Weixin API
	    path = '/'.join([cls.WEIXIN_URL, cls.node])
	    if cls.qiye_flag:
                params = {
                    'corpid': cls.app_id,
                    'corpsecret': cls.app_secret,
                }
	    else:
	        params = {
		    'appid': cls.app_id,
		    'secret': cls.app_secret,
		    'grant_type': cls.grant_type
	        }
	    response = requests.get(path, params=params, verify=False)
	    print response
	    response_info_dict = json.loads(response.text)

	    # store token and expire time
	    app_to_token_dict = {cls.app_id : 
		{
		    'access_token': response_info_dict['access_token'],
		    'expires_in': int(response_info_dict['expires_in']),
		    'fetch_unix_time': unix_now
		}
	    }
	    cls.access_token = response_info_dict['access_token']
	    cls.storage.set_app_to_token_dict(app_to_token_dict)
	    cls.storage.store(logger)
	except Exception as e:
	    logger.exception(e)

    @classmethod
    def get_access_token(cls, logger):
	if not cls._access_token_valid(logger):
	    cls.update_access_token(logger)
	return cls.access_token

