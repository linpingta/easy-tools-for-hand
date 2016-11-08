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
	负责当前Exp检查
	"""
	def __init__(self, exp_id, name, description):
		self._exp_id = int(exp_id)
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
	 负责实验策略的加载和管理
	"""
	strategy_info_dict = {}

	def __init__(self, strategy):
		self._strategy = strategy
		self._origin_handlers = []
	
	def __enter__(self):
		logger = logging.getLogger(__name__)
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
		logger = logging.getLogger(__name__)
		logger.handlers = self._origin_handlers

	@classmethod
	def load(cls, filename, logger):
		""" 加载策略文件"""
		try:
			tree = ET.ElementTree(file=filename)
			root = tree.getroot()
		except IOError, e:
			raise e
		else:
			try:
				exp = tree.getroot()
				for strategy in exp:
					exp_id, name, desc = -1, '', ''
					user_ids, account_ids, campaign_ids, campaign_end_numbers = [], [], [], []
					for elem in strategy.iter():
						if elem.tag == 'name':
							name = elem.text
						if elem.tag == 'exp_id':
							exp_id = elem.text
						if elem.tag == 'desc':
							description = elem.text
						if elem.tag == 'users':
							user_ids = [ int(user) for user in elem.text.split(',') ]
						if elem.tag == 'accounts':
							account_ids = [ int(account) for account in elem.text.split(',') ]
						if elem.tag == 'campaigns':
							campaign_ids = [ int(campaign) for campaign in elem.text.split(',') ]
						if elem.tag == 'campaign_end_numbers':
							campaign_end_numbers = [ int(campaign_end_number) for campaign_end_number in elem.text.split(',') ]
					exp = Exp(exp_id, name, description)
					exp.user_ids = user_ids
					exp.account_ids = account_ids
					exp.campaign_ids = campaign_ids
					exp.campaign_end_numbers = campaign_end_numbers

#					campaign_info = strategy.find('campaigns')
#					if campaign_info is not None:
#						exp.campaign_ids = [ int(campaign) for campaign in campaign_info.text.split(',') ]
#					account_info = strategy.find('accounts')
#					if account_info is not None:
#						exp.account_ids = [ int(account) for account in account_info.text.split(',') ]
#					campaign_end_info = strategy.find('campaign_end_numbers')
#					if campaign_end_info is not None:
#						exp.campaign_end_numbers = [ int(end_number) for end_number in campaign_end_info.text.split(',') ]
					cls.strategy_info_dict[name] = exp
			except Exception, e:
				raise e


if __name__ == '__main__':
	basepath = os.path.abspath(os.getcwd())
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
		format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	)
	logger = logging.getLogger(__name__)

	filename = os.path.join(basepath, 'conf/test_exp.xml')
	try:
		ExpManager.load(filename, logger)
	except IOError as e:
		logger.exception(e)
	else:
		logger.info('work starts')
		# usage
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

			user_info = OrderedDict(user_id=1, account_id=111, campaign_id=1111)
			if exp and exp.has_user(user_info):
				# main logic
				print 'user exists in exp'
				logger.debug('user_id[%d] account_id[%d] campaign_id[%d] participate exp' % tuple(user_info.values()))
			else:
				print 'user not exists in exp'
				logger.debug('user_id[%d] account_id[%d] campaign_id[%d] dont participate exp' % tuple(user_info.values()))

		# usage
		with ExpManager("Mock2") as (exp, logger):
			from collections import OrderedDict
			user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
			if exp and exp.has_user(user_info):
				# main logic
				print 'user exists in exp'
				logger.debug('user_id[%d] account_id[%d] campaign_id[%d] participate exp' % tuple(user_info.values()))
			else:
				print 'user not exists in exp'
				logger.debug('user_id[%d] account_id[%d] campaign_id[%d] dont participate exp' % tuple(user_info.values()))
		logger.info('work ends')
