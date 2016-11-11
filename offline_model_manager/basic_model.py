#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Basic Offline Model"""
__author__ = 'linpingta@163.com'

import os
import sys
import logging
import time
import datetime
import copy
import simplejson as json
try:
	import ConfigParser
    import cPickle as pickle
except ImportError:
	import configparser as ConfigParser
    import pickle

from facebook_interface import FBI
from ts_interface import TSI
from ts_exception import TSIException


class BasicModel(object):
	""" 离线模型的基类
	"""
	def __init__(self, conf):
		self.global_min_age = conf.getint('basic_model', 'global_min_age')
		self.global_max_age = conf.getint('basic_model', 'global_max_age')
		self.TSI = TSI(conf)
		self.ad_client_host = conf.get('db', 'ad_host')
		self.ad_client_port = conf.getint('db', 'ad_port')
		self.stats_client_host = conf.get('db', 'stats_host')
		self.stats_client_port = conf.getint('db', 'stats_port')
		self.user_client_host = conf.get('db', 'user_host')
		self.user_client_port = conf.getint('db', 'user_port')
		
	def _open_ad_client(self):
		''' 连接Ad db，获取广告信息'''
		transport = TSocket.TSocket(self.ad_client_host, self.ad_client_port)
		transport = TTransport.TFramedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		ad_client = TsAdService.Client(protocol)  # Stats in the final
		transport.open()
			
		return (ad_client, transport)

	def _open_stats_client(self):
		''' 链接Stat info, 更新统计数据'''
		stats_transport = TSocket.TSocket(self.stats_client_host, self.stats_client_port)
		stats_transport = TTransport.TFramedTransport(stats_transport)
		stats_protocol = TBinaryProtocol.TBinaryProtocol(stats_transport)
		stats_client = TsStatsService.Client(stats_protocol)  # Stats in the final
		stats_transport.open()
		
		return (stats_client, stats_transport)
	
	def _open_user_client(self):
		''' 连接User db，获取user信息'''
		transport = TSocket.TSocket(self.user_client_host, self.user_client_port)
		transport = TTransport.TFramedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		user_client = TsUserService.Client(protocol)
		transport.open()
			
		return (user_client, transport)

	def _open_clients(self, logger):
		''' 开启客户端, 短连接方式'''
		try:
			logger.debug('open client for adset_creator')
			(self.TSI.ad_client, self.TSI.ad_transport) = self._open_ad_client()
			(self.TSI.stats_client, self.TSI.stats_transport) = self._open_stats_client()
			(self.TSI.user_client, self.TSI.user_transport) = self._open_user_client()
			return 0
		except Exception, e:
			logger.exception(e)
			return -1	

	def init(self, logger):
		""" 初始化"""
		if self._open_clients(logger) < 0:
			raise TSIException("client no open successfully")

	def release(self, logger):
		""" 释放"""
		self.TSI.release(logger)

	def load(self, now, logger):
		""" 加载需要的离线输入"""
		pass

	def dump(self, now, logger):
		""" 保存离线输出"""
		pass

	def run(self, level_object, now, logger):
		""" 针对level_object执行策略逻辑"""
		pass


class FBOperator(object):
	""" 支持FB操作, 目前只应用Campaign级别Model
	"""
	def __init__(self, conf):
		self.FBI = FBI(conf)

	def init_fbi(self, account_id, campaign, now, logger):
		''' 初始化FBI'''
		logger.info('basic_creator init for cpid %d' % campaign.id)
		try:
			(user_client, user_transport) = self._open_user_client()

			# fetch access_token
			rq = RequestHeader()
			rq.requester = "basic_creator"
			rq.operatorUid = 1
			user_access_token_dict = user_client.getAccessTokensByFbUserIds(rq, [ campaign.fb_user_id ])

			# build FBI
			self.FBI.set_session(access_token)

		except Exception, e:
			logger.exception(e)
		finally:
			user_transport.close()
			logger.debug('release client link in INIT')

	def release_fbi(self, logger):
		''' 关闭FBI client'''
		try:
			self.FBI.release(logger)
		except Exception, e:
			logger.exception(e)

