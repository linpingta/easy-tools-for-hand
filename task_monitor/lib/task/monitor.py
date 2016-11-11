#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

"""
Monitor Related Task
"""
__author__ = 'linpingta@163.com'

import os
import sys
sys.path.append("..")
import datetime
import pandas as pd

from base import Task

from facebook_interface import FBI
from ts_interface import TSI


class MonitorTask(Task):
	""" Monitor Task
	"""
	def __init__(self, name, sender=None, object_level='ad', frequency=60, valid=1):
		super(MonitorTask, self).__init__(name, object_level, frequency, valid)
		self._sender = sender
		self.global_sendto_users = []
		self.special_sendto_users = []
		self._start_dt, self._end_dt = 0, 0

	@property
	def sender(self):
		return self._sender

	@sender.setter
	def sender(self, value):
		self._sender = value

	def _get_before_dt(self, dt_now, dt_interval=0):
		""" Used to transfer start/end dt to YYYYMMDD format"""
		dt_before = dt_now + datetime.timedelta(dt_interval)
		return int(dt_before.strftime('%Y%m%d'))

	def _run(self, now, logger):
		print "Hello World"
		return []

	def set_global_sendto_users(self, global_sendto_users):
		self.global_sendto_users = global_sendto_users

	def add_special_sendto_user(self, special_sendto_user):
		self.special_sendto_users.append(special_sendto_user)
	
	def init(self, conf, logger):
		# decide time to check
		try:
			start_dt = conf.getint(self._name, 'start_dt')
			end_dt = conf.getint(self._name, 'end_dt')
		except ValueError:
			logger.info('task[%s] dont define start/end dt' % self._name)
		else:
			try: # judge by formate, only support two, YYYYMMDD or -1 (means 1 day before now)
				datetime.datetime.strptime(str(start_dt), '%Y%m%d')
			except ValueError as e:
				dt_now = datetime.datetime.now()
				self._start_dt = self._get_before_dt(dt_now, start_dt)
				self._end_dt = self._get_before_dt(dt_now, end_dt)
			else:
				self._start_dt = start_dt
				self._end_dt = end_dt

		# set users to send info
		global_sendto_users = conf.get('common', 'global_sendto_users')
		[ self.global_sendto_users.append(user.strip()) for user in global_sendto_users.split(',') ]
		self._FBI = FBI(conf)
		self._TSI = TSI(conf)

	def release(self, logger):
		if self._FBI and isinstance(self._FBI, FBI):
			self._FBI.release(logger)
		if self._TSI and isinstance(self._TSI, TSI):
			self._TSI.release(logger)
		
	def run(self, now, logger):
		""" main task"""
		try:
			# check task info first
			if not self._valid:
				logger.info('task[%s] invalid, return' % self._name)
				return

			logger.info('task[%s] begins' % self._name)

			self._sender.set_sendto_list(self.global_sendto_users + self.special_sendto_users)

			self._sender.add_title(u'Monitor Work [%s]:' % self._name, 1)
			if self._start_dt and self._end_dt:
				self._sender.add_title(u'时间段 %d-%d' % (self._start_dt, self._end_dt))

			result_list = []

			# main work here
			result_list = self._run(now, logger)

			result_df = pd.DataFrame(result_list)
			self._sender.add_table(result_df.to_html(index=False, escape=False))

			self._sender.send(logger)

			logger.info('task[%s] ends' % self._name)
		except Exception as e:
			logger.exception(e)

	def register(self, server, logger):
		""" register itself to monitor server, future to do"""
		pass
