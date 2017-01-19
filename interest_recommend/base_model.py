#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Base Model for hive based train"""
__author__ = 'chutong'

import os
import sys
import time
import datetime
try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser
import logging
import argparse
import pandas as pd
from collections import OrderedDict

from lib.fetcher.hive_fetcher import BaseHiveFetcher
from lib.reader.df_reader import DataFrameReader
from lib.reader.model_reader import ModelReader
from lib.sender.email_sender import EmailSender


class BaseModel(object):
	""" Base Model for train/test on Hive data
	"""
	def __init__(self, basepath, conf):
		self._logname_prefix = conf.get('base_model', 'logname_prefix')
		self._model_name = conf.get('base_model', 'model_name')
		self._model_name = os.path.join(basepath, self._model_name)
		self._resource_name = conf.get('base_model', 'resource_name')
		self._resource_name = os.path.join(basepath, self._resource_name)
		self._hive_fetcher = BaseHiveFetcher(conf)
		self._sender = None
		self._data_reader = None
		self._model_reader = None

	@property
	def sender(self):
		return self._sender

	@sender.setter
	def sender(self, sender):
		self._sender = sender

	@property
	def data_reader(self):
		return self._data_reader

	@data_reader.setter
	def data_reader(self, reader):
		self._data_reader = reader

	@property
	def model_reader(self):
		return self._model_reader

	@model_reader.setter
	def model_reader(self, reader):
		self._model_reader = reader

	def _split_log(self, now, logger):
		""" 拆分日志文件"""
		dt_now = datetime.datetime.fromtimestamp(time.mktime(now))
		dt_1_hour_before = dt_now - datetime.timedelta(hours=1)
		dt_log_s = dt_1_hour_before.strftime('%Y%m%d%H')
		split_log_file = '.'.join([self._logname_prefix, 'bk', dt_log_s])
		logger.debug('dt_now %s, split_log_file %s' % (str(dt_now), split_log_file))
		if not os.path.isfile(split_log_file):
			logger.debug('split log %s' % split_log_file)
			os.system('cp %s %s' % (self._logname_prefix, split_log_file))
			os.system(':>%s' % self._logname_prefix)

	def _load_model(self, logger):
		return self._model_reader.read(self._model_name, logger)

	def _save_model(self, model, logger):
		self._model_reader.dump(model, self._model_name, logger)

	def _make_query(self, dimensions, metrics, filter, having, orderby, limit, now, start_dt, end_dt, logger):
		try:
			self._hive_fetcher.set_dt_interval(now, start_dt, end_dt)
			self._hive_fetcher.set_dimension(dimensions, logger)
			self._hive_fetcher.set_metrics(metrics, logger)
			self._hive_fetcher.set_filter(filter, logger)
			if orderby:
				self._hive_fetcher.set_orderby(orderby, logger)
			if limit > 0:
				self._hive_fetcher.set_limit(limit, logger)
			if having:
				self._hive_fetcher.set_having(having, logger)
			query_str = self._hive_fetcher.generate_query(logger)
			result_rows = self._hive_fetcher.query(query_str, logger)
			logger.info('result rows len %d' % len(result_rows))

			total_dimensions = []
			metric_alias = []
			for metric in metrics:
				if isinstance(metric, dict):
					metric_alias.append(metric.values()[0])
				else:
					metric_alias.append(metric)
			total_dimensions = dimensions + metric_alias
			logger.info('total dimensions %s' % str(total_dimensions))

			d_list = []
			for row in result_rows:
				d = OrderedDict()
				for dimension, row_elem in zip(total_dimensions, row):
					d[dimension] = row_elem
				d_list.append(d)
			if d_list:
				df = pd.DataFrame(d_list)
			else:
				df = pd.DataFrame()
			return df
		except Exception as e:
			logger.exception(e)

	def _fetch_data(self, now, logger):
		return pd.DataFrame()

	def _preprocess_data(self, df, logger):
		return df

	def _get_train_data(self, now, logger):
		logger.info("model train: get train data")
		if self._is_train_reload:
			origin_df = self._fetch_data(now, logger)
			df = self._preprocess_data(origin_df, logger)
			self._data_reader.dump(df, self._resource_name, logger)
		else:
			df = self._data_reader.read(self._resource_name, logger)
		return df

	def _get_train_model(self, df, logger):
		logger.info("model train: get train model")

	def _train(self, now, logger):
		logger.info("model train starts")
		df = self._get_train_data(now, logger)
		return self._get_train_model(df, logger)

	def _test(self, model, logger):
		logger.info("model test starts")

	def init(self, args, logger):
		self._hive_fetcher.init()

		self._is_train = args.train
		self._is_train_reload = args.train_reload
		self._is_test = args.test
		self._is_sent = args.send
		self._start_dt = args.start_dt
		self._end_dt = args.end_dt
		logger.info("init model with train_flag[%d] train_reload_flag[%d] test_flag[%d] send_flag[%d] start_dt[%d] end_dt[%d]" % (self._is_train, self._is_train_reload, self._is_test, self._is_sent, self._start_dt, self._end_dt))

	def run(self, now, logger):

		self._split_log(now, logger)

		if self._is_train:
			model = self._train(now, logger)
			self._save_model(model, logger)
		else:
			model = self._load_model(logger)

		if self._is_test:
			result = self._test(model, logger)
			if self._is_sent:
				self._sender.send(logger)

	def release(self, logger):
		self._hive_fetcher.release()


def _common_parse(parser):
	parser.add_argument("--train", help="whether to run train again", dest="train", action="store_true")
	parser.add_argument("--no-train", help="whether to run train again", dest="train", action="store_false")
	parser.add_argument("--test", help="whether to run test again", dest="test", action="store_true")
	parser.add_argument("--no-test", help="whether to run test again", dest="test", action="store_false")
	parser.add_argument("--train_reload", help="whether to run train_reload again", dest="train_reload", action="store_true")
	parser.add_argument("--no-train_reload", help="whether to run train_reload again", dest="train_reload", action="store_false")
	parser.add_argument("--send", help="whether to run send again", dest="send", action="store_true")
	parser.add_argument("--no-send", help="whether to run send again", dest="send", action="store_false")
	parser.set_defaults(train=False, train_reload=False, test=True, send=False)
	parser.add_argument("--start_dt", help="start date for data fetcher, only for train usage: format YYYYMMDD", default=0, type=int)
	parser.add_argument("--end_dt", help="end date for data fetcher, only for train usage: format YYYYMMDD", default=0, type=int)

def _get_sender(conf, title):
	return EmailSender(conf, title) 

def _get_data_reader(conf):
	return DataFrameReader(conf)

def _get_model_reader(conf):
	return ModelReader(conf)

def main(model_name="base_model", ModelClass=None, _extend_parse=None, title=u"数据分析"):
	model_capital_name = ""
	for part_name in model_name.split("_"):
		model_capital_name += part_name.capitalize()
	basepath = os.path.abspath(sys.path[0])
	confpath = os.path.join(basepath, 'conf/%s.conf' % model_name)
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)

	logging.basicConfig(filename=os.path.join(basepath, "logs/%s.log" % model_name), level=logging.INFO, format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s', datefmt = '%a, %d %b %Y %H:%M:%S')
	logger = logging.getLogger(model_capital_name)

	try:
		parser = argparse.ArgumentParser(prog=model_name, description="run %s for train/test" %  model_name)
		_common_parse(parser)
		_extend_parse(parser)
		args = parser.parse_args()

		engine = ModelClass(basepath, conf)
		engine.sender = _get_sender(conf, title)
		engine.data_reader = _get_data_reader(conf)
		engine.model_reader = _get_model_reader(conf)
		engine.init(args, logger)
		try:
			now = time.localtime()
			engine.run(now, logger)
		except Exception as e:
			logger.exception(e)
		finally:
			engine.release(logger)
	except Exception as e:
		logger.exception(e)

if __name__ == '__main__':
	main("base_model", BaseModel)
