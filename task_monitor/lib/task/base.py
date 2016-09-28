#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' Base Task'''
__author__ = 'linpingta@163.com'


import os, sys
sys.path.append("..")
import datetime
from ts_checker_interface import TSI
from facebook_checker_interface import FBI


class Task(object):
	''' Define Base Task'''
	def __init__(self, object_level='adset', frequency=60, valid=1, name='Task'):
		self.object_level = object_level
		self.frequency = frequency
		self.valid = valid
		self.name = name

		self.TSI = None
		self.FBI = None

	def _load(self, conf, logger):
		pass

	def _dump(self, logger):
		pass

	def _get_before_dt(self, dt_now, dt_interval, logger):
		dt_before = dt_now + datetime.timedelta(dt_interval)
		return int(dt_before.strftime('%Y%m%d'))

	def init(self, conf, logger):
		''' link to db'''
		try:
			self.TSI = TSI()
			self.TSI.init(conf, logger)

			self.FBI = FBI()
			self.FBI.init(conf, logger)

			self._load(conf, logger)

		except Exception as e:
			logger.exception(e)

	def release(self, logger):
		try:
			if self.TSI:
				self.TSI.release(logger)
			if self.FBI:
				self.FBI.release(logger)

			self._dump(logger)

		except Exception as e:
			logger.exception(e)

	def run(self, now, logger):
		''' main task'''
		pass
		
