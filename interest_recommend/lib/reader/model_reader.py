#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

from sklearn.externals import joblib
from base_reader import BaseReader


class ModelReader(BaseReader):
	""" read/dump model with pickle 
	"""
	def read(self, filename, logger):
		logger.info("load model from local %s" % filename)
		return joblib.load(filename)

	def dump(self, model, filename, logger):
		logger.info("save model to local")
		joblib.dump(model, filename)

	
	
