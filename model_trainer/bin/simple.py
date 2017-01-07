#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' simple model caller example'''
__author__ = 'chutong'

import sys, os
import logging
import time, datetime
try:
	import ConfigParser
except:
	import configparser as ConfigParser
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
libpath = os.path.join(basepath, 'lib')
sys.path.append(libpath)

from base_model import TsModel
from external_loader.base_loader import TsLoader
from model_loader.base_loader import TsModelLoader
from cleaner.base_cleaner import TsCleaner


if __name__ == '__main__':

	confpath = os.path.join(basepath, 'conf/simple.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)
	modelconfpath = os.path.join(basepath, 'conf/model_simple.conf')
	model_conf = ConfigParser.RawConfigParser()
	model_conf.read(modelconfpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/simple.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('Simple')

	now = time.localtime()

	m = TsModel(conf)
	m.external_loader = TsLoader()
	m.model_loader = TsModelLoader(model_conf)
	try:
		m.run(now, logger)
	except Exception as e:
		logger.exception(e)

	# use your model to substitue above
	pass
