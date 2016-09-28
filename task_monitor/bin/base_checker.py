#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' Base Checker'''
__author__ = 'linpingta@163.com'

import os, sys
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
sys.path.append(os.path.join(basepath, 'lib'))
import time
import ConfigParser
import logging
from task import MonitorTask 
from sender.email_sender import EmailSender


if __name__ == '__main__':

	basepath = os.path.abspath(os.path.dirname(sys.path[0]))
	confpath = os.path.join(basepath, 'conf/task.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/task.log'), level=logging.INFO,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('BaseChecker')

	email_sender = EmailSender(conf, 'base checker')
	now = time.localtime()
	mt = MonitorTask(email_sender)
	mt.init(conf, logger)
	try:
		mt.run(now, logger)
	except Exception as e:
		logger.exception(e)
	finally:
		mt.release(logger)
	
