#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' base model'''
__author__ = 'chutong'

import os, sys
import time, datetime
import re
import xgboost as xgb

import pandas as pd
import numpy as np
from sklearn.externals import joblib
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV

from external_loader.base_loader import TsLoader


class TsModel(object):
	''' Base Model
	'''
	def __init__(self, conf):
		self.train_filename = conf.get('simple_model', 'train_filename')
		self.test_filename = conf.get('simple_model', 'test_filename')
		self.submission_filename = conf.get('simple_model', 'submission_filename')
		self.model_filename = conf.get('simple_model', 'model_filename')
		self.model_info_filename_prefix = conf.get('simple_model', 'model_info_filename_prefix')

		self.do_train = conf.getboolean('simple_model', 'do_train')
		self.do_search_parameter = conf.getboolean('simple_model', 'do_search_parameter')
		self.do_validate = conf.getboolean('simple_model', 'do_validate')
		self.do_test = conf.getboolean('simple_model', 'do_test')

		self.search_parameter_loss = conf.get('search_parameter', 'search_parameter_loss')
		self.search_parameter_best_score_num = conf.getint('search_parameter', 'search_parameter_best_score_num')
		self.train_loss = conf.get('train_parameter', 'train_loss')
		self.validate_loss = conf.get('validate_parameter', 'validate_loss')

	def _report(self, grid_scores, n_top, logger):
		from operator import itemgetter
		top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
		for i, score in enumerate(top_scores):
			logger.debug("model with rank: {0}".format(i + 1))
			logger.debug("mean validation score: {0:.3f} (std: {1:.3f})".format(
				score.mean_validation_score,
				np.std(score.cv_validation_scores)))
			logger.debug("parameters: {0}".format(score.parameters))

	def _clean_data(self, data, logger):
		''' special clean way should be defined here'''
		return data

	def _load_and_clean_data(self, filename, logger):
		try:
			if not self.external_loader:
				logger.error('model external_loader is not defined')
			else:
				logger.info('model external_loader loads [%s]' % filename)
				data = self.external_loader.load(filename, logger)
				cleaned_data = self._clean_data(data, logger)

				return cleaned_data
		except Exception as e:
			logger.exception(e)
			

	def _generate_combine_and_external_data(self, cleaned_train_data, cleaned_test_data, logger):
		''' sometimes, train and test data need to be combined to generate combined or external data
		'''
		return ((), ())

	def _split_data(self, data, logger):
		''' some data need to be dealt with in different level, for example, different country for demographic analysis, or different species for animal
		'''
		return {'all': data}

	def _transfer_data_to_model(self, splited_key, splited_data, combine_data, external_data, logger):
		''' encode input x/y for model training
		'''
		return (None, None, {})

	def _get_grid_search_model(self, splited_key, logger):
		pass

	def _get_param_grid(self, splited_key, logger):
		pass

	def _do_search_parameter(self, train_x, train_y, splited_key, logger):
		''' grid search related work
		'''
		try:
			clf = self._get_grid_search_model(splited_key, logger)
			param_grid = self._get_param_grid(splited_key, logger)
			if clf and param_grid:
				grid_search = GridSearchCV(clf, scoring=self.search_parameter_loss, param_grid=param_grid)
				grid_search.fit(train_x, train_y)
				self._report(grid_search.grid_scores_, self.search_parameter_best_score_num, logger)
			else:
				logger.error('splited_key[%s] model or parameter grid not defined for search parameter' % splited_key)
		except Exception as e:
			logger.exception(e)

	def _get_model(self, splited_key, logger):
		return self.model_loader.get_model(splited_key, logger)

	def _store_trained_model(self, clf, model_infos, splited_key, logger, scores=None):
		model_splited_dict = {}
		try:
			model_splited_dict = {
				'clf': clf,
				'model_infos': model_infos
			}

			# dump model
			self.model_loader.dump_model(clf, '.'.join([self.model_filename, splited_key]), logger)

			# dump other thing, like encode function
			self.model_loader.dump_model_infos(model_infos, self.model_info_filename_prefix, splited_key, logger)

		except Exception as e:
			logger.exception(e)
		finally:
			return model_splited_dict

	def _do_validation(self, clf, train_x, train_y, splited_key, logger):
		scores = cross_validation.cross_val_score(clf, train_x, train_y, pre_dispatch=1, scoring=self.validate_loss)
		print 'accrucy mean %0.2f +/- %0.2f' % (scores.mean(), scores.std()*2)
		logger.info('splited_key[%s] accrucy mean %0.2f +/- %0.2f' % (splited_key, scores.mean(), scores.std()*2))
		logger.info('splited_key[%s] clf %s' % (splited_key, str(clf)))
		return scores

	def _get_model_names(self, logger):
		return []

	def _load_trained_model(self, splited_key, logger):
		clf = self.model_loader.load_model('.'.join([self.model_filename, splited_key]), logger)
		model_names = self._get_model_names(logger)
		model_infos = self.model_loader.load_model_infos(model_names, self.model_info_filename_prefix, splited_key, logger)
		return (clf, model_infos)

	def _transfer_test_to_model(self, cleaned_test_data, model_dict, combine_data, external_data, logger):
		pass

	def _train(self, clf, train_x, train_y, splited_key, logger):
		logger.info('splited_key[%s] do training' % splited_key)
		clf.fit(train_x, train_y)
		return clf

	def _output_result(self, predict_y, submission_filename, logger):
		pass

	def set_model_loader(self, model_loader, logger):
		self.model_loader = model_loader

	def set_external_loader(self, external_loader, logger):
		self.external_loader = external_loader

	def run(self, now, logger):

		# load and clean data
		cleaned_train_data = self._load_and_clean_data(self.train_filename, logger)
		cleaned_test_data = self._load_and_clean_data(self.test_filename, logger)
		logger.debug('train_data shape %s' % str(cleaned_train_data.shape))
		logger.debug('test_data shape %s' % str(cleaned_test_data.shape))

		# check combine/external data
		(combine_data, external_data) = self._generate_combine_and_external_data(cleaned_train_data, cleaned_test_data, logger)

		model_dict = {}
		# split data in different level, and train them one by one
		splited_data_dict = self._split_data(cleaned_train_data, logger)
		if self.do_train:
			logger.info('do model train...')
			for splited_key, splited_data in splited_data_dict.iteritems():
				logger.info('splited_key[%s] transfer origin data' % splited_key)
				(train_x, train_y, model_infos) = self._transfer_data_to_model(splited_key, splited_data, combine_data, external_data, logger)
				logger.debug('train_x.shape %s' % str(train_x.shape))
				logger.debug('train_y.shape %s' % str(train_y.shape))

				if self.do_search_parameter:
					# GridSearch related work
					logger.info('splited_key[%s] do search parameter' % splited_key)
					self._do_search_parameter(train_x, train_y, splited_key, logger)
				else:
					logger.info('splited_key[%s] do train' % splited_key)
					clf = self._get_model(splited_key, logger)
					if not clf:
						logger.error('splited_key[%s] model not defined' % splited_key)
						continue

					logger.info('splited_key[%s] fit data' % splited_key)
					clf = self._train(clf, train_x, train_y, splited_key, logger)

					# do validtaion
					scores = 0
					if self.do_validate:
						scores = self._do_validation(clf, train_x, train_y, splited_key, logger)

					# store model info
					model_splited_dict = self._store_trained_model(clf, model_infos, splited_key, logger, scores)
					model_dict[splited_key] = model_splited_dict
		else:
			logger.info('load trained model...')
			for splited_key, splited_data in splited_data_dict.iteritems():
				logger.info('splited_key[%s] load trained model' % splited_key)
				# load model info
				(clf, model_infos) = self._load_trained_model(splited_key, logger)

				model_dict[splited_key] = {
					'clf': clf,
					'model_infos': model_infos
				}

		if self.do_test:
			logger.info('load test model...')
			splited_data_dict = self._split_data(cleaned_test_data, logger)
			for splited_key, splited_data in splited_data_dict.iteritems():
				clf = model_dict[splited_key]['clf']
				model_infos = model_dict[splited_key]['model_infos']
				splited_test_x = self._transfer_test_to_model(splited_key, splited_data, model_infos, combine_data, external_data, logger)
				print type(splited_test_x)

				# do prediction
				predict_y = clf.predict(splited_test_x)
				logger.info('splited_key[%s] predict_y.shape %s' % (splited_key, str(predict_y.shape)))
				logger.info('splited_key[%s] predict_y %s' % (splited_key, str(predict_y)))
				self._output_result(predict_y, self.submission_filename, logger)

