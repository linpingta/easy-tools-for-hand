#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

from suite import suite_add_task_module
from suite import DtAction


if __name__ == '__main__':
	try:
		import argparse
		parser = argparse.ArgumentParser(prog="suite", description="run offline data tasks by suite")
		parser.add_argument('-s', '--start_dt', required=True, type=int, action=DtAction, help="start dt of query")
		parser.add_argument('-e', '--end_dt', required=True, type=int, action=DtAction, help="end dt of query")
		args = parser.parse_args()

		if (not args.start_dt) or (not args.end_dt): 
			parser.print_help()
			raise argparse.ArgumentTypeError("start_dt or end_dt not valid")

	except argparse.ArgumentTypeError as e:
		print e
	else:
		# main function
		task_names = ['total_install', 'gender_ratio']
		for task_name in task_names:
			print task_name
			task_id = suite_add_task_module(task_name, args.start_dt, args.end_dt)
			print task_id

