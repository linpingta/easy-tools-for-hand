#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' Basic Offline Model'''
__author__ = 'linpingta@163.com'

import os,sys
import logging
import ConfigParser
import time
import datetime
import copy
import simplejson as json
try:
    import cPickle as pickle
except:
    import pickle

from facebook_interface import FBI
from ts_interface import TSI


class BasicModel(object):
	''' 离线模型的基类
	'''
	def __init__(self, conf):
		self.conf = conf
		self.TSI = None
		self.max_default_cpa = conf.getint('basic_model', 'max_default_cpa')
		self.global_min_age = conf.getint('basic_model', 'global_min_age')
		self.global_max_age = conf.getint('basic_model', 'global_max_age')
		
	def _open_ad_client(self):
		''' 连接Ad db，获取广告信息'''
		ad_client_host = self.conf.get('db', 'ad_host')
		ad_client_port = self.conf.getint('db', 'ad_port')

		transport = TSocket.TSocket(ad_client_host, ad_client_port)
		transport = TTransport.TFramedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		ad_client = TsAdService.Client(protocol)  # Stats in the final
		transport.open()
			
		return (ad_client, transport)

	def _open_stats_client(self):
		''' 链接Stat info, 更新统计数据'''
		stats_client_host = self.conf.get('db', 'stats_host')
		stats_client_port = self.conf.getint('db', 'stats_port')

		stats_transport = TSocket.TSocket(stats_client_host, stats_client_port)
		stats_transport = TTransport.TFramedTransport(stats_transport)
		stats_protocol = TBinaryProtocol.TBinaryProtocol(stats_transport)
		stats_client = TsStatsService.Client(stats_protocol)  # Stats in the final
		stats_transport.open()
		
		return (stats_client, stats_transport)
	
	def _open_user_client(self):
		''' 连接User db，获取user信息'''
		user_client_host = self.conf.get('db', 'user_host')
		user_client_port = self.conf.getint('db', 'user_port')

		transport = TSocket.TSocket(user_client_host, user_client_port)
		transport = TTransport.TFramedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		user_client = TsUserService.Client(protocol)
		transport.open()
			
		return (user_client, transport)

	def open_clients(self, logger):
		''' 开启客户端, 短连接方式'''
		try:
			logger.debug('open client for adset_creator')
			(ad_client, ad_transport) = self._open_ad_client()
			(stats_client, stats_transport) = self._open_stats_client()
			(user_client, user_transport) = self._open_user_client()
			self.TSI.ad_client = ad_client
			self.TSI.ad_transport = ad_transport
			self.TSI.stats_client = stats_client
			self.TSI.stats_transport = stats_transport
			self.TSI.user_client = user_client
			self.TSI.user_transport = user_transport

			return 0
		except Exception, e:
			logger.exception(e)
			return -1	

	def _init_zi(self, now, logger):
		''' 初始化TSI'''
		try:
			logger.info('common interface client starting...')
			(ad_client, ad_transport) = self._open_ad_client()
			(stats_client, stats_transport) = self._open_stats_client()
			(user_client, user_transport) = self._open_user_client()
			logger.info('common interface client started')

			max_repeat_db_num = self.conf.getint('basic_creator', 'MAX_REPEAT_DB_NUM')
			wait_seconds = self.conf.getint('basic_creator', 'WAIT_SECONDS')
			insert_to_db_len = self.conf.getint('basic_creator', 'INSERT_TO_DB_LEN')

			# build TSI
			self.TSI = TSI(ad_client, ad_transport, stats_client, stats_transport, user_client, user_transport, max_repeat_db_num, wait_seconds, insert_to_db_len)

		except Exception, e:
			logger.exception(e)

	def _release_zi(self, logger):
		''' 关闭TSI client'''
		try:
			self.TSI.release(logger)
		except Exception, e:
			logger.exception(e)

	def init(self, now, logger):
		''' 初始化'''
		self._init_zi(now, logger)

	def release(self, logger):
		''' 释放接口'''
		self._release_zi(logger)

	def load(self, now, logger):
		''' 加载需要的离线输入'''
		pass

	def dump(self, now, logger):
		''' 保存离线输出'''
		pass

	def run(self, level_object, now, logger):
		''' 针对level_object执行策略逻辑'''
		pass


class FBOperator(object):
	''' 支持FB操作, 只应用Campaign级别Model
	'''
	def __init__(self, conf):
		self.FBI = None

	def init_fbi(self, account_id, campaign, now, logger):
		''' 初始化FBI'''
		logger.info('basic_creator init for cpid %d' % campaign.id)
		try:
			(user_client, user_transport) = self._open_user_client()

			# fetch access_token
			rq = RequestHeader()
			rq.requester = 'basic_creator'
			rq.operatorUid = 1
			user_access_token_dict = user_client.getAccessTokensByFbUserIds(rq, [ campaign.fb_user_id ])

			# build FBI
			max_repeat_fbi_num = self.conf.getint('basic_creator', 'MAX_REPEAT_FBI_NUM')
			max_adset_num_in_one_batch= self.conf.getint('basic_creator', 'MAX_ADSET_NUM_IN_ONE_BATCH')
			max_bid_ratio = self.conf.getint('basic_creator', 'MAX_BID_RATIO')
			wait_seconds = self.conf.getint('basic_creator', 'WAIT_SECONDS')
			app_id = self.conf.get('FB_Authentication', 'app_id')
			app_secret = self.conf.get('FB_Authentication', 'app_secret')
			self.FBI = FBI(app_id, app_secret, user_access_token_dict[campaign.fb_user_id], max_repeat_fbi_num, wait_seconds, max_adset_num_in_one_batch, max_bid_ratio)

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

