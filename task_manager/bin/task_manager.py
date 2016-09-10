#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

''' Data Explorer'''
__author__='chutong@domob.cn'


import os,sys
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
sys.path.append(os.path.join(basepath, 'lib'))
os.environ.setdefault(
	"DJANGO_SETTINGS_MODULE", "demo.settings"
)
import logging
import ConfigParser
import threading
import Queue
import time
import datetime
import pandas as pd
import numpy as np

from task import *
from models import DemoQueryTask


class TaskThread(threading.Thread):
	def __init__(self, input_queue, output_queue, logger):
		super(TaskThread, self).__init__()
		self.input_queue = input_queue
		self.output_queue = output_queue
		self.logger = logger

	def run(self):
		for task in iter( self.input_queue.get, None):
			try:
				task.run(logger)
				self.output_queue.put(task)
			except Exception as e:
				logger.exception(e)
			finally:
				task.release(logger)
				self.input_queue.task_done()
		self.input_queue.task_done()


class DataExplorer(object):
	''' 负责用户定义任务调度
	'''
	def __init__(self, conf):
		self.logname_prefix = conf.get('task_manager', 'logname_prefix')
		self.result_path = conf.get('task_manager', 'result_path')

		self.hive_host = conf.get('base_hive_fetcher', 'host')
		self.hive_port = conf.getint('base_hive_fetcher', 'port')
		self.hive_db = conf.get('base_hive_fetcher', 'db')

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

	def _task_run(self, input_queue, output_queue, logger):
		for task in iter( input_queue.get, None):
			try:
				task.run(logger)
				output_queue.put(task)
			except Exception as e:
				logger.exception(e)
			finally:
				input_queue.task_done()
		input_queue.task_done()

	def _get_db_tasks(self, now, logger):
		try:
			running_tasks = DemoQueryTask.objects.filter(status=1,paused=0)

			hive_query_tasks = []
			for running_task in running_tasks:
				hive_conn = HiveConnector(self.hive_host, self.hive_port, self.hive_db)
				hive_query_task = HiveQueryTask(running_task, hive_conn, self.result_path)
				if json.loads(running_task.parent_task_ids):
					hive_query_task.set_arguemnt(TopAppArgument, logger)
				else:
					hive_query_task.set_arguemnt(Argument, logger)
				try:
					hive_query_task.init(logger)
				except Exception as e:
					logger.exception(e)
				else:
					hive_query_tasks.append(hive_query_task)
			return hive_query_tasks
		except Exception as e:
			logger.exception(e)

	def _transfer_db_task_name_id_dict(self, db_tasks, logger):
		db_task_name_id_dict = {}
		max_db_task_id = 0
		for db_task in db_tasks:
			if not db_task.name:
				logger.warning('task_id[%d] has no name, no name-id mapping' % db_task.id)
				continue
			db_task_name_id_dict[db_task.name] = db_task.id
			if db_task.id > max_db_task_id:
				max_db_task_id = db_task.id
		return (db_task_name_id_dict, max_db_task_id)

	def _get_user_define_tasks(self, db_tasks, now, logger):
		tasks = []

		# set db task dict
		(db_task_name_id_dict, max_db_task_id) = self._transfer_db_task_name_id_dict(db_tasks, logger)

		db_task_name_id_dict = {}

		# example
		# this is user input
		parent_task_names = []

		parent_task_ids = []
		parent_task_id_name_dict = {}
		for parent_task_name in parent_task_names:
			parent_task_ids.append(db_task_name_id_dict[parent_task_name])
			parent_task_id_name_dict[db_task_name_id_dict[parent_task_name]] = parent_task_name
		user_task = UserDefineTask(1, parent_task_ids, self.result_path, max_db_task_id)
		user_task.set_task_id_name_dict(parent_task_id_name_dict, logger)
		user_task.set_worker(BasicWorker, logger)

		tasks.append(user_task)
		return tasks
		
	def _build_DAG(self, tasks, now, logger):
		task_innode_num_dict = {}
		task_related_tasks_dict = {}
		task_id_dict = {}
		for task in tasks:
			if task.parent_ids:
				[ task_related_tasks_dict.setdefault(parent_id, []).append(task.id) for parent_id in task.parent_ids ]
			task_innode_num_dict[task.id] = len(task.parent_ids) 
			task_id_dict[task.id] = task
		logger.info('task_innode_num_dict %s' % str(task_innode_num_dict))
		logger.info('task_related_tasks_dict %s' % str(task_related_tasks_dict))
		logger.info('task_id_dict %s' % str(task_id_dict))
		return (task_innode_num_dict, task_related_tasks_dict, task_id_dict)

	def _run(self, now, logger):
		''' 遍历tasks，执行查询转换，结果输出'''
		total_tasks = []
		db_tasks = self._get_db_tasks(now, logger)
		total_tasks.extend(db_tasks)

		db_tasks = []
		user_define_tasks = self._get_user_define_tasks(db_tasks, now, logger)
		total_tasks.extend(user_define_tasks)

		# build DAG
		(task_innode_num_dict, task_related_tasks_dict, task_id_dict) = self._build_DAG(total_tasks, now, logger)

		# do tasks
		task_queue = Queue.Queue()
		finished_task_queue = Queue.Queue()
		for task in total_tasks:
			if task.id not in task_innode_num_dict:
				logger.error('task_id[%d] has no innode defined, skip' % task.id)
				continue
			if not task_innode_num_dict[task.id]:
				logger.info('task_id[%d] added to task_queue' % task.id)
				task_queue.put(task)

		threads = []
		for i in range(4):
			threads.append( TaskThread(task_queue, finished_task_queue, logger) )

		for thread in threads:
			thread.daemon = True
			thread.start()

		while 1:
			if not sum(task_innode_num_dict.values()):
				logger.info('all task executed or added to task_queue, break')
				break

			if not finished_task_queue.empty():
				finished_task = finished_task_queue.get()
				logger.info('task_id[%d] finished' % finished_task.id)
				if finished_task.id in task_related_tasks_dict:
					for related_task_id in task_related_tasks_dict[finished_task.id]:
						logger.debug('finished_task_id[%d] with related_task_id[%d]' % (finished_task.id, related_task_id))
						task_innode_num_dict[related_task_id] -= 1
						if not task_innode_num_dict[related_task_id]:
							logger.info('task_id[%d] added to task_queue' % related_task_id)
							task_queue.put(task_id_dict[related_task_id])
				finished_task_queue.task_done()

			logger.info('main thread waiting')
			time.sleep(20)

		for thread in threads:
			task_queue.put(None)

		task_queue.join()

	def run(self, logger):
		''' run()：主函数，根据配置启动服务'''
		try:
			logger.info('data-explorer started')

			# 统一当前时间
			now = time.localtime()

			# 拆分日志文件
			self._split_log(now, logger)

			# 执行操作
			self._run(now, logger)

			logger.info('data-explorer stopped')

		except Exception, e:
			logger.exception(e)


if __name__ == '__main__':

	basepath = os.path.abspath(os.path.dirname(sys.path[0]))
	confpath = os.path.join(basepath, 'conf/task_manager.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/task_manager.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('DataExplorer')

	try:
		DataExplorer(conf).run(logger)	
	except Exception,e:
		logging.exception(e)
