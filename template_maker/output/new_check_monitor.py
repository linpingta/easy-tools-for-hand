#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' NewCheckMonitor Task'''
__author__ = 'linpingta@163.com'


import os, sys
from monitor import MonitorTask
try:
    import cPickle as pickle
except:
    import pickle
import simplejson as json


class NewCheckMonitor(MonitorTask):
    ''' NewCheckMonitor Monitor Task'''
    def __init__(self, sender, object_level, frequency, valid, name):
        super(NewCheckMonitor, self).__init__(sender, object_level, frequency, valid, name)

    def _load(self, conf, logger):
        try:
        	self.new_check_monitor_filename = conf.get('status_monitor', 'new_check_monitor_filename')
            with open(self.new_check_monitor_filename, 'r') as fp_r:
				pass
        except Exception as e:
            logger.exception(e)

    def _dump(self, logger):
        try:
            with open(self.new_check_monitor_filename, 'w') as fp_w:
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
