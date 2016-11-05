#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import os
import sys
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
sys.path.append(os.path.join(basepath, 'task'))
import importlib
import add_task


def suite_add_task_module(module_name, start_dt, end_dt, special_task_name=''):
	try:
		my_module = importlib.import_module(module_name)
		dimensions = my_module.dimensions
		metrics = my_module.metrics
		filters = my_module.filters
		orderby = my_module.orderby
		limit = my_module.limit
		task_name = module_name if not special_task_name else module_name
		return add_task.add_task(task_name, dimensions, metrics, filters, orderby, start_dt, end_dt, limit)
	except ImportError as e:
		print e
	except AttributeError as e:
		print e
	except Exception as e:
		print e
	

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(prog="suite", description="run offline data tasks by suite")
	parser.add_argument('-s', '--start_dt', required=True, type=int, help="start dt of query")
	parser.add_argument('-e', '--end_dt', required=True, type=int, help="end dt of query")
	args = parser.parse_args()

	try:
		from datetime import datetime
		s = datetime.strptime(str(args.start_dt), '%Y%m%d')
		e = datetime.strptime(str(args.end_dt), '%Y%m%d')
	except ValueError as e:
		print e
	else:

		# main function
		task_id = suite_add_task_module('base', args.start_dt, args.end_dt)
		print task_id

