#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import time
import logging
try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser


class HiveConn(object):
	""" HiveConn should be replaced with real working one
	here just for mock
	"""
	def __init__(self, host, port, db):
		pass


class BaseHiveFetcher(HiveConn):
	""" Base Hive Fetcher
	"""
	def __init__(self, conf):
		host = conf.get('base_hive_fetcher', 'host')
		port = conf.getint('base_hive_fetcher', 'port')
		db = conf.get('base_hive_fetcher', 'db')
		HiveConn.__init__(self, host, port, db)

		self.conn = None
		self.start_dt = 0
		self.end_dt = 0
		self.dimensions = []
		self.metrics = []
		self.orderby = []
		self.tablename = 'my_offline_data'
		self.limit = -1
		self.arguments = []
		self.having = []

	def init(self):
		self.conn = self.getConn()
		self.cur = self.conn.cursor()

	def release(self):
		if self.conn:
			self.releaseConn(self.conn)

	def set_dt_interval(self, now, start_dt=0, end_dt=0):
		if not start_dt:
			start_dt = 0
		if not end_dt:
			end_dt = int(time.strftime('%Y%m%d', now))
		self.start_dt = start_dt
		self.end_dt = end_dt

	def set_dimension(self, dimensions, logger):
		self.dimensions = dimensions 

	def set_metrics(self, metrics, logger):
		self.metrics = metrics

	def set_orderby(self, orderby, logger):
		if not self.metrics:
			raise Exception('no metric defined')
		metric_alias = []
		for metric in self.metrics:
			if isinstance(metric, dict):
				metric_alias.append(metric.values()[0])
			else:
				metric_alias.append(metric)
		#for orderby_metric in orderby:
		#	if orderby_metric not in metric_alias:
		#		raise Exception('orderby metric %s not defined in metrics %s' % (orderby_metric, str(self.metrics)))
		self.orderby = orderby

	def set_limit(self, limit, logger):
		self.limit = limit

	def set_filter(self, where, logger):
		self.filter = where

	def set_having(self, having, logger):
		self.having = having

	def generate_query(self, logger):
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

		if self.having:
			having_str = ' having '
			tmp_str = ' and '.join(self.having)
			having_str = having_str + tmp_str
			base_query_str += having_str

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
		logger.info('generated query str: %s' % query_str)
		return query_str

	def query(self, sql, logger):
		try:
			self.cur.execute(sql)
			return self.cur.fetch()
		except Exception as e:
			logger.exception(e)
