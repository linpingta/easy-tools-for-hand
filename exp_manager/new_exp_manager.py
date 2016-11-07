# -*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

__author__ = 'linpingta@163.com'

import os
import sys
import logging
try:
	import ConfigParser
	import xml.etree.cElementTree as ET
except ImportError:
	import configparser as ConfigParser
	import xml.etree.ElementTree as ET
import copy


class Exp(object):
	"""
	负责当前Exp
	"""
	def __init__(self, exp_id, name, description):
		self._exp_id = exp_id
		self._name = name
		self._description = description
		self._campaign_ids = []
		self._account_ids = []
		self._user_ids = []
		self._campaign_end_numbers = []

	@property
	def id(self):
		return self._exp_id

	@property
	def name(self):
		return self._name

	@property
	def user_ids(self):
		return self._user_ids

	@user_ids.setter
	def user_ids(self, value):
		self._user_ids = value

	@property
	def account_ids(self):
		return self._account_ids

	@account_ids.setter
	def account_ids(self, value):
		self._account_ids = value

	@property
	def campaign_ids(self):
		return self._campaign_ids

	@campaign_ids.setter
	def campaign_ids(self, value):
		self._campaign_ids = value

	@property
	def campaign_end_numbers(self):
		return self._campaign_end_numbers

	@campaign_end_numbers.setter
	def campaign_end_numbers(self, value):
		self._campaign_end_numbers = value

	def has_user(self, user_info={}):
		try:
			user_attribute_list = ['user_id', 'account_id', 'campaign_id', 'campaign_end_number']
			user_info_n = copy.copy(user_info)
			user_info_n['campaign_end_number'] = user_info_n['campaign_id'] % 10
			for user_attribute in user_attribute_list:
				class_attribute = '_' + user_attribute + 's'
				if user_info_n[user_attribute] in self.__dict__[class_attribute]:	
					return True
			return False
		except KeyError as e:
			raise e


class ExpManager(object):
	"""
	 负责AAM实验策略的加载和管理
	"""
	strategy_info_dict = {}

	def __init__(self, strategy):
		self._strategy = strategy
		self._origin_handlers = []
	
	def __enter__(self):
		logger = logging.getLogger()
		if self._strategy in self.strategy_info_dict:
			exp = self.strategy_info_dict[self._strategy]
			self._origin_handlers = logger.handlers
			logger.handlers = []
			ch = logging.StreamHandler(sys.stdout)
			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(expid)s - %(expname)s')
			ch.setFormatter(formatter)
			logger.addHandler(ch)
			extra = {'expid':exp.id, 'expname':exp.name}
			logger = logging.LoggerAdapter(logger, extra)
			return (exp, logger)
		else:
			logger.error('strategy %s not defined in exp, error' % self._strategy)
			return (None, logger)

	def __exit__(self, exc_type, exc_value, exc_tb):
		pass

	@classmethod
	def load(cls, filename, logger):
		""" 加载策略文件"""
		try:
			tree = ET.ElementTree(file=filename)
		except IOError, e:
			logger.exception(e)
		else:
			try:
				exp = tree.getroot()
				for strategy in exp:
					name = strategy.find('name').text
					exp_id = strategy.find('exp_id').text
					description = strategy.find('desc').text
					exp = Exp(exp_id, name, description)
					campaign_info = strategy.find('campaigns')
					if campaign_info is not None:
						exp.campaign_ids = [ int(campaign) for campaign in campaign_info.text.split(',') ]
					account_info = strategy.find('accounts')
					if account_info is not None:
						exp.account_ids = [ int(account) for account in account_info.text.split(',') ]
					campaign_end_info = strategy.find('campaign_end_numbers')
					if campaign_end_info is not None:
						exp.campaign_end_numbers = [ int(end_number) for end_number in campaign_end_info.text.split(',') ]
					cls.strategy_info_dict[name] = exp
			except Exception, e:
				logger.exception(e)


if __name__ == '__main__':
	basepath = os.path.abspath(os.getcwd())
	logging.basicConfig(filename=os.path.join(basepath, 'logs/mock.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('ExpManager')

	filename = os.path.join(basepath, 'conf/dummy_exp.xml')
	ExpManager.load(filename, logger)

	with ExpManager("Mock") as (exp, logger):
		from collections import OrderedDict
		user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
		if exp and exp.has_user(user_info):
			# main logic
			print 'user exists in exp'
			logger.debug('user_id[%d] account_id[%d] campaign_id[%d] participate exp' % tuple(user_info.values()))
		else:
			print 'user not exists in exp'
			logger.debug('user_id[%d] account_id[%d] campaign_id[%d] dont participate exp' % tuple(user_info.values()))
