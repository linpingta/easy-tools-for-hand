#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

from suite import suite_add_task_module


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
		task_names = ['total_install', 'gender_ratio']
		for task_name in task_names:
			print task_name
			task_id = suite_add_task_module(task_name, args.start_dt, args.end_dt)
			print task_id

