#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Shelter animal prediction"""
__author__ = 'chutong'

import os
import sys
import logging
import time, datetime
try:
	import ConfigParser
except ImportError:
	import configparser as ConfigParser
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
libpath = os.path.join(basepath, 'lib')
sys.path.append(libpath)

from shelter_common_model import ShelterCommonModel
from external_loader.csv_loader import TsCsvLoader
from model_loader.xgboost_model import XgboostModel
from model_loader.randomforest_model import RandomForestModel
from cleaner.shelter_cleaner import ShelterCleaner


if __name__ == '__main__':

	# common cfg
	confpath = os.path.join(basepath, 'conf/simple.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)

	# model parameter cfg
	modelconfpath = os.path.join(basepath, 'conf/model_simple.conf')
	model_conf = ConfigParser.RawConfigParser()
	model_conf.read(modelconfpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/shelter.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('Shelter')

	now = time.localtime()

	m = ShelterCommonModel(conf)
	m.external_loader = TsCsvLoader()
	m.model_loader = XgboostModel(model_conf)
	m.model_loader = RandomForestModel(model_conf)
	m.data_cleaner = ShelterCleaner()
	try:
		m.run(now, logger)
	except Exception as e:
		logger.exception(e)
