#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

""" 
Facebook API Interface
"""
__author__ = 'linpingta@163.com'

import os
import sys
try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser

from facebookads import FacebookSession
from facebookads import FacebookAdsApi
from facebookads.objects import (
	AdUser,
)


class FBI(object):
    """ 
	包装Facebook Python API的调用接口
	"""
    me = AdUser(fbid='me') # user account

    def __init__(self, conf):
        self.app_id = conf.get('FB_Authentication', 'app_id')
        self.app_secret = conf.get('FB_Authentication', 'app_secret')
        self._max_repeat_fbi_num = conf.getint('fbi', 'MAX_REPEAT_FBI_NUM')
        self._max_adset_num_in_one_batch= conf.getint('fbi', 'MAX_ADSET_NUM_IN_ONE_BATCH')
        self._max_bid_ratio = conf.getint('fbi', 'MAX_BID_RATIO')
        self._wait_seconds = conf.getint('fbi', 'WAIT_SECONDS')
        
    def set_session(self, access_token):
        """' 构造Session，创建API"""
        self.session = FacebookSession(self.app_id, self.app_secret, access_token)
        self.api = FacebookAdsApi(self.session)
        self.access_token = access_token
        FacebookAdsApi.set_default_api(self.api)

	def release(self, logger):
		pass

	def do_ad_work(self, ad_id, logger):
		try:
			pass
		except Exception as e:
			logger.exception(e)

