#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' Basic Offline Model Manager'''
__author__ = 'linpingta@163.com'

import os,sys
import logging
import ConfigParser
import time
import datetime
try:
    import cPickle as pickle
except:
    import pickle


class BasicModelManager(object):
	''' 离线模型基类
	'''
	def __init__(self, conf):
		self.conf = conf
		self._call_wait_hours = 1 # default run interval

	def _split_log(self, now, logger):
		''' 拆分日志文件'''
		dt_now = datetime.datetime.fromtimestamp(time.mktime(now))
		dt_1_hour_before = dt_now - datetime.timedelta(hours=1)
		dt_log_s = dt_1_hour_before.strftime('%Y%m%d%H')
		split_log_file = '.'.join([self.logname_prefix, 'bk', dt_log_s])
		logger.debug('dt_now %s, split_log_file %s' % (str(dt_now), split_log_file))
		if not os.path.isfile(split_log_file):
			logger.debug('split log %s' % split_log_file)
			os.system('cp %s %s' % (self.logname_prefix, split_log_file))
			os.system(':>%s' % self.logname_prefix)

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

	def _release_ad_client(self, ad_transport):
		''' 关闭ad client'''
		ad_transport.close()

	def _create_model(self, logger):
		''' Model创建'''
		pass

	def _init_model(self, now, logger):
		''' Model初始化处理'''
		pass

	def _store_model(self, now, logger):
		''' Model保存'''
		pass

	def _release_model(self, logger):
		''' Model释放处理'''
		pass

	def _wait(self, logger):
		time.sleep(3600 * self._call_wait_hours)

	def _run(self, data_level_object, now, logger):
		''' 针对每个data_level_object的模型应用'''
		pass

	def run(self, logger, run_once=False):
		''' 主程序'''
		try:
			self._create_model(logger)

			while True:

				logger.info('common interface client starting...')
				try:
					(ad_client, ad_transport) = self._open_ad_client()
					logger.info('common interface client started')
				except Exception, e:
					logger.exception(e)
				else:

					# 统一当前时间
					now = time.localtime()

					# 拆分日志文件
					self._split_log(now, logger)

					# 加载模型
					self._init_model(now, logger)

					# 管理运行
					try:
						self._manager_run(ad_client, now, logger)
					except Exception, e:
						logger.exception(e)
					else:
						# 保存模型设置
						self._store_model(now, logger)

					# 释放模型
					self._release_model(logger)

				finally:
					self._release_ad_client(ad_transport)

				if run_once:
					break

				self._wait(logger)

			logger.info('BasicModelManger Finish')
		except Exception, e:
			logger.exception(e)


class CampaignAllLevel(object):
	''' Campaign级别分组管理
	'''
	def _manager_run(self, ad_client, now, logger):
		''' Campaign运行'''
		# read active campaigns
		rq = RequestHeader()
		rq.operatorUid = 1
		rq.requester = 'basic_campaign_model'
		auto_account_campaign_dict = ad_client.getAccountWithCampaigns(rq, int(time.mktime(now)), 1)

		logger.info('campaign manager run started')
		logger.info('auto accounts len %d' % (len(auto_account_campaign_dict.keys()) ))

		for account_id, campaigns in auto_account_campaign_dict.iteritems():
			logger.info('account_id %d campaigns len %d' % (account_id, len(campaigns)))
			logger.info('read auto campaigns in aid %d' % account_id)

			[ self._run(account_id, campaign, now, logger) for campaign in campaigns ]
		logger.info('campaign manager run finished')


class CampaignLevel(object):
	''' Campaign级别分组管理
	'''
	def _manager_run(self, ad_client, now, logger):
		''' Campaign运行'''
		# read active campaigns
		rq = RequestHeader()
		rq.operatorUid = 1
		rq.requester = 'basic_campaign_model'
		auto_account_campaign_dict = ad_client.getAccountWithCampaignsInSystemStatus(rq, int(time.mktime(now)), int(time.mktime(now)))

		logger.info('campaign manager run started')
		logger.info('auto accounts len %d' % (len(auto_account_campaign_dict.keys()) ))

		for account_id, campaigns in auto_account_campaign_dict.iteritems():
			logger.info('account_id %d campaigns len %d' % (account_id, len(campaigns)))
			logger.info('read auto campaigns in aid %d' % account_id)

			[ self._run(account_id, campaign, now, logger) for campaign in campaigns ]
		logger.info('campaign manager run finished')


class CampaignNoAccountLevel(object):
	''' Campaign级别分组管理
	'''
	def _manager_run(self, ad_client, now, logger):
		''' Campaign运行'''
		# read active campaigns
		rq = RequestHeader()
		rq.operatorUid = 1
		rq.requester = 'basic_campaign_model'
		auto_account_campaign_dict = ad_client.getAccountWithCampaignsInSystemStatus(rq, int(time.mktime(now)), int(time.mktime(now)))

		logger.info('campaign no-account manager run started')
		logger.info('auto accounts len %d' % (len(auto_account_campaign_dict.keys()) ))

		for account_id, campaigns in auto_account_campaign_dict.iteritems():
			logger.info('account_id %d campaigns len %d' % (account_id, len(campaigns)))
			logger.info('read auto campaigns in aid %d' % account_id)

			[ self._run(campaign, now, logger) for campaign in campaigns ]
		logger.info('campaign no-account manager run finished')


class PromotionLevel(object):
	''' Promotion级别分组管理
	'''
	def _manager_run(self, ad_client, now, logger):
		''' Promotion运行'''
		rq = RequestHeader()
		rq.operatorUid = 1
		rq.requester = 'basic_promotion_model'

		# no interface interface to get all promotion directly now, accomplish with two steps
		auto_account_campaign_dict = ad_client.getAccountWithCampaignsInSystemStatus(rq, int(time.mktime(now)), int(time.mktime(now)))
		
		logger.info('promotion manager run started')
		logger.info('auto accounts len %d' % (len(auto_account_campaign_dict.keys()) ))
	
		promotions = []	
		promotion_ids = []
		for account_id, campaigns in auto_account_campaign_dict.iteritems():

			[ promotion_ids.append(campaign.promotion_id) for campaign in campaigns if campaign.promotion_id not in promotion_ids ]

		promotions = ad_client.getPromotionsByIds(rq, promotion_ids)

		# no account info needed for Promotion level
		# as no FB operation permitted
		[ self._run(promotion, now, logger) for promotion in promotions ]
		logger.info('promotion manager run finished')


class AccountLevel(object):
	''' Account级别分组管理
	'''
	def _manager_run(self, ad_client, now, logger):
		''' Account运行'''
		rq = RequestHeader()
		rq.operatorUid = 1
		rq.requester = 'basic_account_model'

		auto_account_campaign_dict = ad_client.getAccountWithCampaignsInSystemStatus(rq, int(time.mktime(now)), int(time.mktime(now)))

		logger.info('account manager run started')
		logger.info('auto accounts len %d' % (len(auto_account_campaign_dict.keys()) ))

		for account_id, campaigns in auto_account_campaign_dict.iteritems():
			strategy_campaign_inside = False
			for campaign in campaigns:
				if (not campaign.paused) and campaign.status and campaign.is_system_status:
					strategy_campaign_inside = True
					break
			if strategy_campaign_inside:
				self._run(account_id, now, logger)

		logger.info('account manager run finished')


if __name__ == '__main__':

	basepath = os.path.abspath(os.path.dirname(sys.path[0]))
	confpath = os.path.join(basepath, 'conf/strategy_model.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/basic_model.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('BasicModel')

	try:
		BasicModelManager(conf).run(logger)
	except Exception,e:
		logging.exception(e)

