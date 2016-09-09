# -*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import os,sys
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
import logging
import ConfigParser
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET


class ExpManager(object):
	''' 负责AAM实验策略的加载和管理
	'''
	exp_campaigns_dict = {}
	exp_accounts_dict = {}
	exp_id_dict = {}
	exp_campaign_end_dict = {}

	def __init__(self):
		pass

	@classmethod
	def get_exp_id(cls, strategy_name, logger):
		exp_id = 0
		try:
			exp_id = cls.exp_id_dict[strategy_name]
		except Exception, e:
			logger.exception(e)
		finally:
			return exp_id

	@classmethod
	def strategy_exists(cls, strategy_name, logger):
		return strategy_name in cls.exp_id_dict

	@classmethod
	def account_strategy_exists(cls, strategy_name, logger):
		''' 指定名称的策略是否存在'''
		return strategy_name in cls.exp_accounts_dict

	@classmethod
	def campaign_strategy_exists(cls, strategy_name, logger):
		''' 指定名称的策略是否存在'''
		return strategy_name in cls.exp_campaigns_dict

	@classmethod
	def account_in_strategy(cls, strategy_name, fb_account_id, logger):
		''' campaign存在于strategy生效的campaign列表'''
		if cls.account_strategy_exists(strategy_name, logger):
			if -1 in cls.exp_accounts_dict[strategy_name]: # all account used for this strategy
				logger.debug('strategy account valid for all')
				return True
			else:
				logger.debug('strategy account ids %s' % str(cls.exp_accounts_dict[strategy_name]))
				return fb_account_id in cls.exp_accounts_dict[strategy_name]
		else:
			logger.debug('strategy %s not defined' % strategy_name)
			return False

	@classmethod
	def campaign_in_strategy(cls, strategy_name, campaign_id, logger):
		''' campaign存在于strategy生效的campaign列表'''
		if cls.campaign_strategy_exists(strategy_name, logger):
			if -1 in cls.exp_campaigns_dict[strategy_name]: # all campaign used for this strategy
				logger.debug('strategy campaign valid for all')
				return True
			else:
				logger.debug('strategy campaign ids %s' % str(cls.exp_campaigns_dict[strategy_name]))
				return campaign_id in cls.exp_campaigns_dict[strategy_name]
		else:
			logger.debug('strategy %s not defined' % strategy_name)
			return False

	@classmethod
	def campaign_end_number_in_strategy(cls, strategy_name, campaign_id, logger):
		''' campaign存在于strategy生效的campaign列表'''
		if cls.strategy_exists(strategy_name, logger):
			end_numbers = cls.exp_campaign_end_dict[strategy_name]
			end_number_flag = False
			for end_number in end_numbers:
				if not ((campaign_id - end_number) % 10):
					end_number_flag = True
					break
			return end_number_flag
		else:
			logger.error('strategy %s not defined' % strategy_name)
			return False

	@classmethod
	def load(cls, filename, logger):
		''' 加载策略文件'''
		try:
			tree = ET.ElementTree(file=filename)
		except Exception, e:
			logger.exception(e)
		else:
			try:
				exp = tree.getroot()
				for strategy in exp:
					name = strategy.find('name').text
					exp_id = strategy.find('exp_id').text
					campaign_info = strategy.find('campaigns')
					if campaign_info is not None:
						campaigns = [ int(campaign) for campaign in campaign_info.text.split(',') ]
						cls.exp_campaigns_dict.setdefault(name, campaigns)
					account_info = strategy.find('accounts')
					if account_info is not None:
						accounts = [ int(account) for account in account_info.text.split(',') ]
						cls.exp_accounts_dict.setdefault(name, accounts)
					campaign_end_info = strategy.find('campaign_end_numbers')
					if campaign_end_info is not None:
						campaign_end_numbers = [ int(end_number) for end_number in campaign_end_info.text.split(',') ]
						cls.exp_campaign_end_dict.setdefault(name, campaign_end_numbers)
					cls.exp_id_dict.setdefault(name, int(exp_id))
				logger.info('load account_info %s' % str(cls.exp_accounts_dict))
				logger.info('load campaign_info %s' % str(cls.exp_campaigns_dict))
				logger.info('load campaign_end_info %s' % str(cls.exp_campaign_end_dict))
				logger.info('load exp_id %s' % str(cls.exp_id_dict))
			except Exception, e:
				logger.exception(e)


if __name__ == '__main__':

	# test ExpManager
	basepath = os.path.abspath(os.getcwd())
	filename = os.path.join(basepath, 'conf/dummy_exp.xml')

	logging.basicConfig(filename=os.path.join(basepath, 'logs/mock.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('ExpManager')

	try:
		ExpManager.load(filename, logger)
		print ExpManager.campaign_in_strategy('Mock', 1234, logger)
		print ExpManager.campaign_in_strategy('Mock', 12345, logger)
		print ExpManager.campaign_in_strategy('Mock2', 1234, logger)
		print ExpManager.campaign_in_strategy('Mock2', 12345, logger)
		print ExpManager.account_in_strategy('Mock2', 12345, logger)
		print ExpManager.campaign_end_number_in_strategy('TimeWithCPA', 19875, logger)
		print ExpManager.campaign_end_number_in_strategy('TimeWithCPA', 19878, logger)
	except Exception, e:
		logger.exception(e)
