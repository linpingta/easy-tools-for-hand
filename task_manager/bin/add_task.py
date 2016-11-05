#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import os
import sys
os.environ.setdefault(
	"DJANGO_SETTINGS_MODULE", "demo.settings"
)
import time
import simplejson as json

from models import DemoQueryTask


def add_task(name, dimensions, metrics, filters, orderby, start_dt, end_dt, limit=-1, input_parent_task_ids=[]):

	# common task setting
	paused = 0
	status = 1
	create_time = int(time.time())
	parent_task_ids = json.dumps(input_parent_task_ids)
	tablename = 'demo_offline_data'

	dimension = json.dumps(dimensions)
	metric = json.dumps(metrics)
	filter = json.dumps(filters)
	order = json.dumps(orderby)

	if limit > 0:
		task = DemoQueryTask(
			name=name,
			paused=paused,
			status=status,
			create_time=create_time,
			start_dt=start_dt,
			end_dt=end_dt,
			order=order,
			filter=filter,
			metric=metric,
			limit=limit,
			dimension=dimension,
			tablename=tablename,
			parent_task_ids=parent_task_ids
		)
	else:
		task = DemoQueryTask(
			name=name,
			paused=paused,
			status=status,
			create_time=create_time,
			start_dt=start_dt,
			end_dt=end_dt,
			order=order,
			filter=filter,
			metric=metric,
			dimension=dimension,
			tablename=tablename,
			parent_task_ids=parent_task_ids
		)
	task.save()
	return task.id


if __name__ == '__main__':

	start_dt = 20160601
	end_dt = 20160731

	# example task
	dimensions = ['people', 'age']
	metrics = ['impressions', 'spend', 'clicks', 'mobile_app_install', {'1000*sum(spend)/sum(impressions)':'cpm'}, {'sum(spend)/sum(mobile_app_install)':'cpa'}, {'100*sum(clicks)/sum(impressions)':'ctr'}, {'100*sum(mobile_app_install)/sum(clicks)':'cvr'}]
	filters = [
		'people != ""',
		'age != ""',
	]
	orderby = []
	add_task('example', dimensions, metrics, filters, orderby, start_dt, end_dt)

