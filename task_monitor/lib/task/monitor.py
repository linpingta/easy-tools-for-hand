#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' Base Task'''
__author__ = 'linpingta@163.com'


import os, sys
from base import Task


class MonitorTask(Task):
	''' Monitor Task'''
	def __init__(self, sender=None, object_level='object', frequency=60, valid=1, name='Task'):
		super(MonitorTask, self).__init__(object_level, frequency, valid, name)
		self.sender = sender
		self.new_mailto_list = []

	def _get_ad_objects(self, now, logger):
		return []

	def _get_ad_headinfo(self, logger):
		return []

	def run(self, now, logger):
		''' main task'''
		try:
			# check task info first
			if not self.valid:
				logger.info('task[%s] invalid, return' % self.name)
				return

			logger.info('task[%s] begins' % self.name)

			# ad_objects as list of list
			ad_headinfo = self._get_ad_headinfo(logger)
			ad_objects = self._get_ad_objects(now, logger)

			if (not ad_objects) or (not ad_headinfo) or (len(ad_headinfo) != len(ad_objects[0])):
				logger.error('task[%s] ad_info_format illegal' % self.name)
				return

			# send info
			if self.new_mailto_list:
				self.sender.add_to_mailto_list(self.new_mailto_list, logger)
			self.sender.send(ad_headinfo, ad_objects, now, logger)

			logger.info('task[%s] ends' % self.name)
		except Exception as e:
			logger.exception(e)
