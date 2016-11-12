#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

""" Data Task"""
__author__ = 'chutong'

import os,sys
import time
import datetime
import pandas as pd
from collections import OrderedDict
import simplejson as json
import re

from hive_conn import HiveConnector
from argument import EmptyArgument, TopAppArgument


class BasicTask(object):
	def __init__(self, id, parent_ids = [], result_path='', name=''):
		self.id = id
		self.parent_ids = parent_ids
		self.result_path = result_path
		self.name = name
		# define an empty df
		self.df = pd.DataFrame() 
		self._argument = None

	def _dump_df(self, logger):
		if self.df.empty:
			logger.warning('task_id[%d]: df is empty, dump an empty one' % self.id)
		if self.result_path:
			self.df.to_csv(os.path.join(self.result_path, 'result_%d.csv' % self.id), header=True)
			self.df.to_csv(os.path.join(self.result_path, 'result_%s.csv' % (self.name)), header=True)
		else:
			self.df.to_csv('result_%d.csv' % self.id, header=True)
			self.df.to_csv('result_%s.csv' % (self.name), header=True)

	def init(self, logger):
		pass

	def run(self, logger):
		logger.info('basic task {0}'.format(self.id))

	def release(self, logger):
		self._dump_df(logger)


class HiveQueryTask(BasicTask):
	def __init__(self, demo_query_task, hiveconn=None, result_path=''):
		parent_ids = json.loads(demo_query_task.parent_task_ids) if demo_query_task.parent_task_ids else []
		super(HiveQueryTask, self).__init__(demo_query_task.id, parent_ids, result_path, demo_query_task.name)

		self.status = demo_query_task.status
		self.paused = demo_query_task.paused
		self.dimensions = json.loads(demo_query_task.dimension) if demo_query_task.dimension else []
		if not self.dimensions:
			self.dimensions = ['1']
		self.metrics = json.loads(demo_query_task.metric) if demo_query_task.metric else []
		self.filter = json.loads(demo_query_task.filter) if demo_query_task.filter else []
		self.orderby = json.loads(demo_query_task.order) if demo_query_task.order else []
		self.start_dt = demo_query_task.start_dt
		self.end_dt = demo_query_task.end_dt
		if not self.start_dt:
			self.start_dt = 0
		if not self.end_dt:
			self.end_dt = int(time.strftime('%Y%m%d', time.localtime()))
		self.limit = demo_query_task.limit if demo_query_task.limit else 0
		self.create_time = demo_query_task.create_time
		self.tablename = demo_query_task.tablename

		# link to hive instance
		self.hive_conn = hiveconn 
		self.conn = None

		# store query result
		self.df = None

	def _init_hive(self, logger):
		self.conn =  self.hive_conn.getConn()
		self.cur = self.conn.cursor()

	def _release_hive(self, logger):
		if self.conn:
			self.hive_conn.releaseConn(self.conn)

	def _check(self, logger):
		if self.orderby and (not self.metrics):
			raise Exception('no metric defined')
		
		metric_alias = []
		for metric in self.metrics:
			if isinstance(metric, dict):
				metric_alias.append(metric.values()[0])
			else:
				metric_alias.append(metric)

		#for orderby_metric in self.orderby:
		#	if orderby_metric not in metric_alias:
		#		raise Exception('orderby metric %s not defined in metrics %s' % (orderby_metric, str(self.metrics)))

	def _generate_query(self, logger):
		query_str = ''
		dimension_str = ','.join(self.dimensions)
		groupby_str = dimension_str

		if not self.filter:
			where_str = ' AND '.join(['dt >= %d' % self.start_dt, 'dt <= %d' % self.end_dt])
		else:
			self.filter.extend(['dt >= %d' % self.start_dt, 'dt <= %d' % self.end_dt])
			where_str = ' AND '.join(self.filter)

		metric_str = ''
		for idx, metric in enumerate(self.metrics):
			if idx > 0:
				metric_str += ','
			if isinstance(metric, dict):
				metric_func = metric.keys()[0]
				metric_alias = metric[metric_func]
				metric_str += '%s as %s' % (metric_func, metric_alias)
			else:
				metric_str += 'sum(%s) as %s' % (metric, metric)

		if metric_str:
			base_query_str = ' '.join(['select', dimension_str, ',', metric_str, 'from', self.tablename, 'where', where_str, 'group by', groupby_str])
		else:
			base_query_str = ' '.join(['select', dimension_str, 'from', self.tablename, 'where', where_str, 'group by', groupby_str])

		if self.orderby:
			orderby_str = ' order by ' 
			for idx, orderby in enumerate(self.orderby):
				if idx > 0:
					orderby_str += ','
				orderby_str += (' %s ' % orderby)
			orderby_str += ' desc '
			base_query_str += orderby_str 

		if self.limit > 0:
			limit_str = ' limit %d ' % self.limit
			base_query_str += limit_str

		# replace arguments if necessary
		if self.arguments:
			for argument in self.arguments:
				base_query_str = base_query_str.replace("***", argument)
		query_str = base_query_str
		logger.info('task_id[%d] generated query str: %s' % (self.id, query_str))
		self.query_str = query_str

	def set_arguemnt(self, argument, logger):
		self._argument = argument

	def init(self, logger):
		# init hive
		self._init_hive(logger)

	def run(self, logger):
		logger.info('task_id[%d] make query' % self.id)

		# set arguments if needed
		if self._argument:
			self.arguments = self._argument.get(self.result_path, self.parent_ids, logger)

		# do examine on task first, no need to query for illegal input
		self._check(logger)

		# generate query
		self._generate_query(logger)

		self.cur.execute(self.query_str)

		dimensions = self.dimensions
		metric_alias = []
		for metric in self.metrics:
			if isinstance(metric, dict):
				metric_alias.append(metric.values()[0])
			else:
				metric_alias.append(metric)
		dimensions.extend(metric_alias)
		logger.info('task_id[%d] dimension & metric names: %s' % (self.id, str(dimensions)))
	
		result_rows = self.cur.fetch()
		logger.info('task_id[%d] result rows len[%d]' % (self.id, len(result_rows)))

		d_list = []
		for row in result_rows:
			d = OrderedDict()
			for dimension, row_elem in zip(dimensions, row):
				d[dimension] = row_elem
			d_list.append(d)
		self.df = pd.DataFrame(d_list)

	def release(self, logger):
		super(HiveQueryTask, self).release(logger)
		self._release_hive(logger)


class UserDefineTask(BasicTask):
	""" 用户自定义任务
	"""
	def __init__(self, id, parent_ids = [], result_path='', max_db_task_id=0, name=''):
		id = id + (max_db_task_id + 1)* 10
		super(UserDefineTask, self).__init__(id, parent_ids, result_path)

		self.name = name
		self.parent_df_dict = {}

	def _run(self, name_df_dict, logger):
		pass

	def set_task_id_name_dict(self, parent_task_id_name_dict, logger):
		self.parent_task_id_name_dict = parent_task_id_name_dict

	def set_worker(self, worker, logger):
		self.worker = worker

	def run(self, logger):

		for parent_id in self.parent_ids:
			df = pd.read_csv(os.path.join(self.result_path, 'result_%d.csv' % parent_id))
			parent_name = self.parent_task_id_name_dict[parent_id]
			self.parent_df_dict[parent_name] = df

		try:
			self.df = self.worker.do(self.parent_df_dict, logger)
		except Exception as e:
			logger.exception(e)


class BasicWorker(object):

	@classmethod
	def do(cls, name_df_dict, logger):
		logger.info('Basic Worker do')
		return pd.DataFrame()
