#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' {{ model_capital_name }} Task'''
__author__ = '{{ author }}@domob.cn'


import os, sys
from monitor import MonitorTask
try:
    import cPickle as pickle
except:
    import pickle
import simplejson as json


class {{ model_capital_name }}(MonitorTask):
    ''' {{ model_capital_name }} Monitor Task'''
    def __init__(self, sender, object_level, frequency, valid, name):
        super({{ model_capital_name }}, self).__init__(sender, object_level, frequency, valid, name)

    def _load(self, conf, logger):
        try:
        	self.{{ model_name }}_filename = conf.get('status_monitor', '{{ model_name }}_filename')
            with open(self.{{ model_name }}_filename, 'r') as fp_r:
				pass
        except Exception as e:
            logger.exception(e)

    def _dump(self, logger):
        try:
            with open(self.{{ model_name }}_filename, 'w') as fp_w:
				pass
        except Exception as e:
            logger.exception(e)

    def _get_ad_headinfo(self, logger):
		return []

    def _get_ad_objects(self, now, logger):
        ''' real main function'''
        ad_objects = []
        try:
			pass
        except Exception as e:
            logger.exception(e)
        finally:
            return ad_objects

