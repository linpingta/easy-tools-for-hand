#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' xgboost model'''
__author__ = 'chutong'

from joblib_loader import TsJoblibModelLoader
from xgboost.sklearn import XGBClassifier


class XgboostModel(TsJoblibModelLoader):
	''' Xgboost Model
	'''
	def __init__(self, model_conf):
		super(XgboostModel, self).__init__(model_conf)

		self.learning_rate = model_conf.getfloat('xgboost', 'learning_rate')
		self.n_estimators = model_conf.getint('xgboost', 'n_estimators')
		self.max_depth = model_conf.getint('xgboost', 'max_depth')
		self.seed = model_conf.getint('xgboost', 'seed')
		self.subsample = model_conf.getfloat('xgboost', 'subsample')
		self.colsample_bytree = model_conf.getfloat('xgboost', 'colsample_bytree')
		self.objective = model_conf.get('xgboost', 'objective')
		self.nthread = model_conf.getint('xgboost', 'nthread')

	def get_model(self, splited_key, logger):
		return XGBClassifier(learning_rate=self.learning_rate, n_estimators=self.n_estimators, max_depth=self.max_depth, subsample=self.subsample, colsample_bytree=self.colsample_bytree, seed=self.seed, objective=self.objective, nthread=self.nthread, silent=False)
