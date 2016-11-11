#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Feature Reader"""
__author__ = 'linpingta@163.com'

import os
import sys
import logging
import re
import time
import datetime
try:
	import ConfigParser
    import cPickle as pickle
except:
	import configparser as ConfigParser
    import pickle

# from sklearn import linear_model
import numpy as np


class ModelReader(object):
	""" 输入adset，按相应规则编码，读取预测结果
	"""
	def __init__(self, conf):
		self.conf = conf
		self.last_update = 0

	def init(self, logger):
		""" 初始化"""
		try:
			pass
		except Exception, e:
			logger.exception(e)

	def release(self, logger):
		""" 释放相关资源"""
		try:
			pass
		except Exception, e:
			logger.exception(e)

	def time_to_load(self, now, logger):
		""" 需要更新模型的时间间隔"""
		# default only load once
		if not self.last_update:
			return True
		return False

	def _load(self, now, logger):
		""" 加载模型"""
		return 1

	def load(self, now, logger):
		""" 加载模型"""
		try:
			return_flag = self._load(now, logger)
		except Exception, e:
			logger.exception(e)
		finally:
			self.last_update = now
			return return_flag

	def read_by_adset(self, ts_adset, ts_campaign, now, logger):
		""" 在Adset级别读取模型输出"""
		pass

	def read_by_campaign(self, ts_campaign, now, logger):
		""" 在Campaign级别读取模型输出"""
		pass


class ClassficationModelReader(ModelReader):
	""" 读取regression模型输出
	"""
	def __init__(self, level, conf):
		super(ClassficationModelReader, self).__init__(conf)
		self.model_dict = {}
		self.check_dict = {}
		self.model_level = level
		self.global_min_age = conf.getint('feature_encoder', 'global_min_age')
		self.global_max_age = conf.getint('feature_encoder', 'global_max_age')
		self.model_prefix = conf.get('feature_classfication_trainer', 'model_prefix')
		self.check_prefix = conf.get('feature_manager', 'feature_checker_prefix')
		self._enlarge_feature_weight = conf.getint('feature_encoder', 'enlarge_feature_weight')
		self._load_hours = conf.getint('feature_classfication_trainer', 'load_hours')

	def _load_parameter_and_checker(self, ts_campaign, now, logger):
		""" 加载参数"""
		query_key = ts_campaign.id if self.model_level == 'ts_campaign_id' else ts_campaign.promotion_id

		logger.debug('campaign_id[%d] read model info in level %s with query_key %s' % (ts_campaign.id, self.model_level, query_key))
		if query_key not in self.model_dict:
			logger.debug('model_level %s key %d dont have data in offline model' % (self.model_level, query_key))
			return (None, {})
		if query_key not in self.check_dict:
			logger.debug('model_level %s key %d dont have data in offline check' % (self.model_level, query_key))
			return (None, {})

		model_parameter = self.model_dict[query_key]
		check_parameter = self.check_dict[query_key]
		#logger.debug('model_parameter %s' % str(model_parameter))
		#logger.debug('check_parameter %s' % str(check_parameter))
		return (model_parameter, check_parameter)

	def _encode_adset(self, ts_adset, check_parameter, ad_client, now, logger):
		""" 对输入adset做编码"""
		attribute_list = []
		try:
			creative_q_dict = check_parameter['creative_id']
			#interest_q_dict = check_parameter['interest']
			gender_q_dict = check_parameter['gender']
			location_q_dict = check_parameter['location']
			img_q_dict = check_parameter['img']
			txt_q_dict = check_parameter['txt']

			rq = RequestHeader()
			rq.request = 'strategy_model'
			rq.operatorUid = 1
			try:
				ts_ad = ad_client.getAdByAdsetId(rq, ts_adset.id)
			except:
				raise Exception('creative not defined for adset')

			if self.model_level == 'ts_campaign_id':
				creative_idx_list = [0] * (len(creative_q_dict) + 1)
				if ts_ad.ts_creative_id in creative_q_dict:
					creative_idx_list[creative_q_dict[ts_ad.ts_creative_id]] = 1
				attribute_list.extend(creative_idx_list)
			elif self.model_level == 'promotion_id__2':
				# encode img/text id here
				img_and_txt = ad_client.getImagesAndTextsByCreativeIds(rq, [ ts_ad.ts_creative_id ])
				img_in_creative = img_and_txt.imageLibs[0]
				txt_in_creative = img_and_txt.creativeTextLibs[0]
				if (img_in_creative.fb_image_id not in img_q_dict) or (txt_in_creative.id not in txt_q_dict):
					logger.debug('fb_img_id[%s] or txt_id[%s] not defined in offline model' % (str(img_in_creative.fb_image_id), str(txt_in_creative.id)))
					return []

				img_idx_list = [0] * (len(img_q_dict) + 1)
				img_idx_list[img_q_dict[img_in_creative.fb_image_id]] = 1
				attribute_list.extend(img_idx_list)
				txt_idx_list = [0] * (len(txt_q_dict) + 1)
				txt_idx_list[txt_q_dict[txt_in_creative.id]] = 1
				attribute_list.extend(txt_idx_list)

			gender_idx_list = [0] * (len(gender_q_dict) + 1)
			if ts_adset.gender in gender_q_dict:
				gender_idx_list[gender_q_dict[ts_adset.gender]] = 1
			weight_gender_idx_list = gender_idx_list * self._enlarge_feature_weight
			attribute_list.extend(weight_gender_idx_list)

			age_idx_list = [0] * (self.global_max_age - self.global_min_age + 1)
			ad_min_age = ts_adset.min_age
			ad_max_age = ts_adset.max_age
			age_idx_list[ad_min_age - self.global_min_age : ad_max_age - self.global_min_age + 1] = [1] * (ad_max_age - ad_min_age + 1)
			attribute_list.extend(age_idx_list)

			location_idx_list = [0] * (len(location_q_dict) + 1)
			if ts_adset.location in location_q_dict:
				location_idx_list[location_q_dict[ts_adset.location]] = 1
			weight_location_idx_list = location_idx_list * self._enlarge_feature_weight
			attribute_list.extend(weight_location_idx_list)

		except Exception, e:
			logger.exception(e)
		finally:
			return attribute_list

	def _load(self, now, logger):
		""" 加载模型文件和查询字典"""
		try:
			model_file = '_'.join([self.model_prefix, self.model_level])
			logger.debug('load model from file %s' % model_file)
			with open(model_file, 'r') as fp_r_pickle:
				self.model_dict = pickle.load(fp_r_pickle)

			check_file = '_'.join([self.check_prefix, self.model_level])
			logger.debug('load check from file %s' % check_file)
			with open(check_file, 'r') as fp_r_pickle:
				self.check_dict = pickle.load(fp_r_pickle)
		except Exception, e:
			logger.exception(e)
			return -1
		return 1

	def time_to_load(self, now, logger):
		""" 需要更新模型的时间间隔"""
		if not self.last_update:
			return True
		load_minutes = int(self._load_hours * 60)
		return datetime.datetime.fromtimestamp(time.mktime(now)) - datetime.datetime.fromtimestamp(time.mktime(self.last_update)) >= datetime.timedelta(minutes=load_minutes)

	def read_by_adset(self, ts_adset, ts_campaign, ad_client, now, logger):
		""" 读取regression模型输出"""
		# find model parameter
		(model_parameter, check_parameter) = self._load_parameter_and_checker(ts_campaign, now, logger)

		if (model_parameter is None) or (not str(check_parameter)):
			logger.debug('adset_id[%d] model load failed' % ts_adset.id)
			return -1

		# encode input adset
		adset_encoded_attribute_list = self._encode_adset(ts_adset, check_parameter, ad_client, now, logger)

		# check model
		if len(adset_encoded_attribute_list) != len(model_parameter.coef_[0]):
			logger.debug('adset_id[%d] encoded_len %d <> model_parameter_len %d, failed' % (ts_adset.id, len(adset_encoded_attribute_list), len(model_parameter.coef_[0])))
			return -1

		result_prob = model_parameter.predict_proba(adset_encoded_attribute_list)
		(neg_prob, pos_prob) = result_prob[0]
		logger.debug('adset id[%d] train neg_prob %f pos_prob %f' % (ts_adset.id, neg_prob, pos_prob))
		return pos_prob

