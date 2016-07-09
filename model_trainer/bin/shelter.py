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
from shelter_common_model import ShelterCommonModel
from external_loader.csv_loader import TsCsvLoader
from model_loader.xgboost_model import XgboostModel
from model_loader.randomforest_model import RandomForestModel


if __name__ == '__main__':

	basepath = os.path.abspath(os.path.dirname(sys.path[0]))
	confpath = os.path.join(basepath, 'conf/shelter.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)
	modelconfpath = os.path.join(basepath, 'conf/model_shelter.conf')
	model_conf = ConfigParser.RawConfigParser()
	model_conf.read(modelconfpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/shelter.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('shelter')

	now = time.localtime()

	m = ShelterCommonModel(conf)
	m.set_external_loader(TsCsvLoader(), logger)
	m.set_model_loader(XgboostModel(model_conf), logger)
	#m.set_model_loader(RandomForestModel(model_conf), logger)
	try:
		m.run(now, logger)
	except Exception as e:
		logger.exception(e)
