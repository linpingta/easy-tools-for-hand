#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :


""" Element With Business Logic"""
__author__ = "chutong"


from abc import ABCMeta, abstractmethod

from domob_pyutils.ive2_helper import HiveConn
from models import ZeusQueryTask
from task import HiveQueryTask


class BaseQuery(object):
	"""
	Base data query class
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def query(self, logger):
		""" Query data and return DataFrame"""
		pass


class HiveTaskQuery(BaseQuery):
	""" Query data from hive with task_id
	"""
	def __init__(self, task_id, hive_host, hive_port, hive_db, result_path=None):
		self._task_id = task_id
		self.hive_conn = HiveConn(hive_host, hive_port, result_path)
		if not result_path: # use current directory if not told
			self.result_path = os.getcwd()
		else:
			self.result_path = result_path

	@property
	def task_id(self):
		return self._task_id

	@task_id.setter
	def task_id(self, task_id):
		self._task_id = task_id

	def query(self, logger):
		try:
			zeus_task = ZeusQueryTask.objects.get(id=self._task_id)
			if not zeus_task:
				logger.error("task_id[%d] not defined in zeus task db, return")
				return
			hive_query_task = HiveQueryTask(zeus_task, self.hive_conn, self.result_path) 
			try:
				hive_query_task.init(logger)
			except IOError as e:
				logger.exception(e)
			else:
				try;
					hive_query_task.run(logger)
				except Exception as e:
					logger.exception(e)
				finally:
					hive_query_task.release(logger)
			return hive_query_task.df
		except Exception as e:
			logger.exception(e)


class DFQuery(BaseQuery):
	""" 
	Query data from dataframe path
	"""
	def __init__(self, data_path):
		self.data_path = data_path

	def query(self, logger):
		try:
			return pd.read_csv(self.data_path)
		except Exception as e:
			logger.exception(e)


class DataQueryFactory(object):
	"""
	Build data query handler
	"""
	@classmethod
	def build(cls, type, value, conf=None):
		if type == 'task':
			hive_host = conf.get("db", "hive_host")
			hive_port = conf.get("db", "hive_port")
			hive_db = conf.get("db", "hive_db")
			return HiveTaskQuery(value, hive_host, hive_port, hive_db)
		elif type == 'df':
			return DFQuery(value)
		else:
			raise ValueError("both task_id and data_path empty, illegal")
		
