#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

''' Facebook API'''
__author__ = 'linpingta@163.com'

import os, sys

from facebookads import FacebookSession
from facebookads import FacebookAdsApi
from facebookads.objects import (
    AdUser,
    AdAccount,
    Campaign,
    AdSet,
    Ad,
    AdCreative,
    TargetingSpecsField,
)
from facebookads.specs import ObjectStorySpec, LinkData, AttachmentData

import ConfigParser
import pprint
from functools import partial
import time
import copy
import simplejson as json
import requests

def visit_fb(func):
    def _wrapper(self, logger, func_type, *args, **kw):
        fbi_repeat_num = 0
        while fbi_repeat_num < self._max_repeat_fbi_num:
            return_val = func(self, *args, **kw)
            if isinstance(return_val, int):
                if return_val >= 0:
                    break
            elif isinstance(return_val, basestring):
                if not return_val:
                    break
            else:
                logger.warning('no return_val defined in %s' % func_type)
            fbi_repeat_num = fbi_repeat_num + 1
            logger.warning('fail to %s in the [%d] try, try again after [%d] seconds' % (func_type, fbi_repeat_num, self._wait_seconds))
            time.sleep(self._wait_seconds)
            
        if fbi_repeat_num >= self._max_repeat_fbi_num:
            logger.error('failed to %s with %s' % (func_type, str(return_val)))
            raise Exception('%s failed' % func_type)    
        return 
    return _wrapper


class FBI(object):
    me = AdUser(fbid='me') # user account

    ''' 包装facebook python API的调用接口'''
    def init(self, conf, logger):
        self.app_id = conf.get('FB_Authentication', 'app_id')
        self.app_secret = conf.get('FB_Authentication', 'app_secret')
        self._max_repeat_fbi_num = conf.getint('fbi', 'MAX_REPEAT_FBI_NUM')
        self._max_adset_num_in_one_batch= conf.getint('fbi', 'MAX_ADSET_NUM_IN_ONE_BATCH')
        self._max_bid_ratio = conf.getint('fbi', 'MAX_BID_RATIO')
        self._wait_seconds = conf.getint('fbi', 'WAIT_SECONDS')
        
    def set_session(self, access_token):
        ''' 构造session，创建api'''
        self.session = FacebookSession(self.app_id, self.app_secret, access_token)
        self.api = FacebookAdsApi(self.session)
        self.access_token = access_token
        FacebookAdsApi.set_default_api(self.api)

    def release(self, logger):
        ''' clear work'''
        pass
    
