#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

""" 
{{ model_capital_name }} Task
"""
__author__ = '{{ author }}@163.com'


import os
import sys
try:
    import cPickle as pickle
except:
    import pickle
import simplejson as json


from monitor import MonitorTask


class {{ model_capital_name }}(MonitorTask):
    """ 
	{{ model_capital_name }} Monitor Task
	"""
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
		""" monitor headers"""
		return []

    def _get_ad_objects(self, now, logger):
        """ monitor body, fetch from FBI/DBI"""
        ad_objects = []
        try:
			pass
        except Exception as e:
            logger.exception(e)
        finally:
            return ad_objects

