#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Base Model"""
__author__ = 'chutong'

import os
import sys
import time
import datetime
import re

import xgboost as xgb
import pandas as pd
import numpy as np

from sklearn.externals import joblib
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV


class TsModel(object):
	""" Basic Model for feature engineering / training testing
	"""
	def __init__(self, conf):
		self._train_filename = conf.get('simple_model', 'train_filename')
		self._test_filename = conf.get('simple_model', 'test_filename')
		self._submission_filename = conf.get('simple_model', 'submission_filename')
		self._model_filename = conf.get('simple_model', 'model_filename')
		self._model_info_filename_prefix = conf.get('simple_model', 'model_info_filename_prefix')

		self._do_train = conf.getboolean('simple_model', 'do_train')
		self._do_search_parameter = conf.getboolean('simple_model', 'do_search_parameter')
		self._do_validate = conf.getboolean('simple_model', 'do_validate')
		self._do_test = conf.getboolean('simple_model', 'do_test')

		self._encode_type = conf.get('encoder', 'encode_type')

		self._search_parameter_loss = conf.get('search_parameter', 'search_parameter_loss')
		self._search_parameter_best_score_num = conf.getint('search_parameter', 'search_parameter_best_score_num')
		self._validate_loss = conf.get('validate_parameter', 'validate_loss')

		self._external_loader = None
		self._model_loader = None
		self._data_cleaner = None

	def _report(self, grid_scores, n_top, logger):
		from operator import itemgetter
		top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
		for i, score in enumerate(top_scores):
			logger.debug("model with rank: {0}".format(i + 1))
			logger.debug("mean validation score: {0:.3f} (std: {1:.3f})".format(
				score.mean_validation_score,
				np.std(score.cv_validation_scores)))
			logger.debug("parameters: {0}".format(score.parameters))

	def _load_data(self, filename, logger):
		if not self._external_loader:
			raise ValueError('model external_loader not defined')

		logger.info('model external_loader loads data from file [%s]' % filename)
		data = self._external_loader.load(filename, logger)

		return data

	def _clean_data(self, data, logger):
		if not self._data_cleaner:
			raise ValueError('model data_cleaner not defined')

		logger.info('model data_cleaner clean data')
		cleaned_data = self._data_cleaner.clean(data, logger)

		return cleaned_data

	def _generate_combine_data(self, cleaned_train_data, cleaned_test_data, logger):
		""" sometimes, train and test data need to be combined to generate combined data
		"""
		pass

	def _load_external_data(self, logger):
		""" sometimes, we may use external data for training"""
		pass

	def _split_data(self, data, logger):
		""" some data need to be dealt within different level, for example, different country for demographic analysis, or different species for animal
		"""
		return {'all': data}

	def _encode_feature(self, splited_key, train_data, test_data, external_data, logger):
		""" encode input x/y for model training
		"""
		return (None, None, None, {})

	def _get_grid_search_model(self, splited_key, logger):
		return self._model_loader.get_model(splited_key, logger)

	def _get_param_grid(self, splited_key, logger):
		return {}

	def _grid_search(self, train_x, train_y, splited_key, logger):
		""" grid search related work
		"""
		try:
			clf = self._get_grid_search_model(splited_key, logger)
			param_grid = self._get_param_grid(splited_key, logger)
			if clf and param_grid:
				grid_search = GridSearchCV(estimator=clf, scoring=self._search_parameter_loss, param_grid=param_grid)
				grid_search.fit(train_x, train_y)
				self._report(grid_search.grid_scores_, self._search_parameter_best_score_num, logger)
			else:
				logger.error('splited_key[%s] model or parameter grid not defined for search parameter' % splited_key)
		except Exception as e:
			logger.exception(e)

	def _get_model(self, splited_key, logger):
		return self._model_loader.get_model(splited_key, logger)

	def _store_trained_model(self, clf, model_infos, splited_key, logger, scores=None):
		model_splited_dict = {}
		try:
			model_splited_dict = {
				'clf': clf,
				'model_infos': model_infos
			}

			# dump model
			self._model_loader.dump_model(clf, '.'.join([self._model_filename, splited_key]), logger)

			# dump other thing, like encode function
			self._model_loader.dump_model_infos(model_infos, self._model_info_filename_prefix, splited_key, logger)

		except Exception as e:
			logger.exception(e)
		finally:
			return model_splited_dict

	def _do_validation(self, clf, train_x, train_y, splited_key, logger):
		scores = cross_validation.cross_val_score(clf, train_x, train_y, pre_dispatch=1, scoring=self._validate_loss)
		logger.info('splited_key[%s] accrucy mean %0.2f +/- %0.2f' % (splited_key, scores.mean(), scores.std()*2))
		logger.info('splited_key[%s] clf %s' % (splited_key, str(clf)))
		return scores

	def _get_model_names(self, logger):
		return []

	def _load_trained_model(self, splited_key, logger):
		clf = self._model_loader.load_model('.'.join([self._model_filename, splited_key]), logger)
		model_names = self._get_model_names(logger)
		model_infos = self._model_loader.load_model_infos(model_names, self._model_info_filename_prefix, splited_key, logger)
		return (clf, model_infos)

	def _train(self, clf, train_x, train_y, splited_key, logger):
		logger.info('splited_key[%s] do training' % splited_key)
		clf.fit(train_x, train_y)
		return clf

	def _report_feature_importance(self, clf, train_x, logger):
		importances = clf.feature_importances_
		indices = np.argsort(importances)[::-1]
		for f in range(train_x.shape[1]):
			logger.info("%d. feature_name %s feature %d (%f)" % (f+1, train_x.columns[indices[f]], indices[f], importances[indices[f]]))

	def _predict(self, clf, test_x, splited_key, logger):
		return clf.predict(test_x)

	def _output(self, predict_y, submission_filename, logger):
		np.savetxt(submission_filename, predict_y, delimiter=',')

	def _output(self, predict_y, submission_filename, logger):
		""" output result to submit"""
		pass

	@property
	def model_loader(self):
		return self._model_loader

	@model_loader.setter
	def model_loader(self, value):
		self._model_loader = value

	@property
	def external_loader(self):
		return self._external_loader

	@external_loader.setter
	def external_loader(self, value):
		self._external_loader = value

	@property
	def data_cleaner(self):
		return self._data_cleaner

	@data_cleaner.setter
	def data_cleaner(self, value):
		self._data_cleaner = value

	def run(self, now, logger):
		""" model train and test"""

		# load and clean data
		cleaned_train_data = self._clean_data(self._load_data(self._train_filename, logger), logger)
		logger.debug('train_data shape %s' % str(cleaned_train_data.shape))

		cleaned_test_data = self._clean_data(self._load_data(self._test_filename, logger), logger)
		logger.debug('test_data shape %s' % str(cleaned_test_data.shape))

		# load external data if necessary
		external_data = self._load_external_data(logger)

		model_dict = {}

		# split data in different level, and train them one by one
		splited_train_data_dict = self._split_data(cleaned_train_data, logger)
		splited_test_data_dict = self._split_data(cleaned_test_data, logger)

		for splited_key in splited_train_data_dict.keys():
			splited_train_data = splited_train_data_dict[splited_key]
			if splited_key not in splited_test_data_dict:
				logger.error('splited_key[%s] has no test data' % splited_key)
				continue

			splited_test_data = splited_test_data_dict[splited_key]

			logger.info('splited_key[%s] encode origin data' % splited_key)
			(train_x, train_y, test_x, model_infos) = self._encode_feature(splited_key, splited_train_data, splited_test_data, external_data, logger)
			logger.debug('train_x.shape %s' % str(train_x.shape))
			logger.debug('train_y.shape %s' % str(train_y.shape))
			logger.debug('test_x.shape %s' % str(test_x.shape))

			if self._do_train:
				logger.info('do model train...')

				if self._do_search_parameter:
					# GridSearch related work
					logger.info('splited_key[%s] do search parameter' % splited_key)
					self._grid_search(train_x, train_y, splited_key, logger)
				else:
					logger.info('splited_key[%s] do train' % splited_key)
					clf = self._get_model(splited_key, logger)
					#if not clf:
					if clf is None:
						logger.error('splited_key[%s] model not defined' % splited_key)
						continue

					logger.info('splited_key[%s] fit data' % splited_key)

					scores = 0
					# do validtaion
					if self._do_validate:
						scores = self._do_validation(clf, train_x, train_y, splited_key, logger)
					else:
						clf = self._train(clf, train_x, train_y, splited_key, logger)

						# feature importances
						self._report_feature_importance(clf, train_x, logger)

						# store model info
						model_splited_dict = self._store_trained_model(clf, model_infos, splited_key, logger, scores)
						model_dict[splited_key] = model_splited_dict
			else:
				logger.info('load trained model...')
				logger.info('splited_key[%s] load trained model' % splited_key)
				# load model info
				(clf, model_infos) = self._load_trained_model(splited_key, logger)

				model_dict[splited_key] = {
					'clf': clf,
					'model_infos': model_infos
				}

			if self._do_test:
				logger.info('load test model...')
				clf = model_dict[splited_key]['clf']

				# do prediction
				predict_y = self._predict(clf, test_x, splited_key, logger)
				logger.info('splited_key[%s] predict_y.shape %s' % (splited_key, str(predict_y.shape)))
				logger.info('splited_key[%s] predict_y %s' % (splited_key, str(predict_y)))
				self._output(predict_y, self._submission_filename, logger)

