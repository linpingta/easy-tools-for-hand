#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

"""
Global Scheduler
"""
__author__ = 'linpingta@163.com'

from __future__ import absolute_import
from celery import Celery
from celery.schedules import crontab


app = Celery('monitors',
	broker='redis://localhost',
	backend='redis://localhost',
	include=['base_checker']
	)

app.conf.update(
	CELERYBEAT_SCHEDULE = {
		"base": {
			"task": "base_checker.main",
			"schedule": crontab(minute="*/1"),
			"args": (),
		}
	}
)
