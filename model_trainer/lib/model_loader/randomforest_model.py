#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' xgboost model'''
__author__ = 'chutong'

from joblib_loader import TsJoblibModelLoader
from sklearn.ensemble import RandomForestClassifier


class RandomForestModel(TsJoblibModelLoader):
	''' RandomForest Model
	'''
	def __init__(self, model_conf):
		super(RandomForestModel, self).__init__(model_conf)

		self.sub_tree_num = model_conf.getint('random_forest_classifier', 'sub_tree_num')
		self.max_depth_num = model_conf.getint('random_forest_classifier', 'max_depth_num')

	def get_model(self, splited_key, logger):
		return RandomForestClassifier(n_estimators=self.sub_tree_num, max_depth=self.max_depth_num, verbose=True)
