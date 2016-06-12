#-*- coding: utf-8 -*-
''' simple model example'''
__author__ = 'chutong'

import time, datetime
import re

import pandas as pd
import numpy as np
from sklearn.externals import joblib
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV

class TsModel(object):
    ''' Base Model
    '''  
    def __init__(self, conf):
        self.train_filename = conf.get('simple_model', 'train_filename')
        self.test_filename = conf.get('simple_model', 'test_filename')
        self.submission_filename = conf.get('simple_model', 'submission_filename')
	self.do_train = conf.getboolean('simple_model', 'do_train')
	self.do_search_parameter = conf.getboolean('simple_model', 'do_search_parameter')
	self.do_validate = conf.getboolean('simple_model', 'do_validate')
	self.do_test = conf.getboolean('simple_model', 'do_test')
	self.store_model = conf.getboolean('simple_model', 'store_model')

	self.search_parameter_loss = conf.get('search_parameter', 'search_parameter_loss')
	self.search_parameter_best_score_num = conf.getint('search_parameter', 'search_parameter_best_score_num')
	self.train_loss = conf.get('train_parameter', 'train_loss')
	self.validate_loss = conf.get('validate_parameter', 'validate_loss')

    def _report(self, grid_scores, n_top, logger):
	from operator import itemgetter
        top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
        for i, score in enumerate(top_scores):
            print("Model with rank: {0}".format(i + 1))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  score.mean_validation_score,
                  np.std(score.cv_validation_scores)))
            print("Parameters: {0}".format(score.parameters))
            print("")
            logger.debug("Model with rank: {0}".format(i + 1))
            logger.debug("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  score.mean_validation_score,
                  np.std(score.cv_validation_scores)))
            logger.debug("Parameters: {0}".format(score.parameters))

    def _load_and_clean_data(self, filename, logger):
	pass

    def run(self, now, logger):

	# load and clean data
	cleaned_train_data = self._load_and_clean_data(self.train_filename, logger)
	cleaned_test_data = self._load_and_clean_data(self.test_filename, logger)

	# check combine/external data
	(combine_data, external_data) = self._generate_combine_external_data(cleaned_train_data, cleaned_test_data, logger)

	model_dict = {}
	splited_data_dict = self._split_data(cleaned_train_data, logger)
	if self.do_train:
	    logger.info('do model train...')
	    for splited_key, splited_data in splited_data_dict.iteritems():
	    	(train_x, train_y, model_infos) = self._transfer_data_to_model(splited_key, splited_data, combine_data, external_data, logger)
		if self.do_search_parameter:
		    # GridSearch related work
		    logger.info('splited_key[%s] do search parameter' % splited_key)
		    clf = self._get_grid_search_model(splited_key, logger)
		    param_grid = self._get_param_grid(splited_key, logger)
		    grid_search = GridSearchCV(clf, scoring=self.search_parameter_loss, param_grid=param_grid)
		    grid_search.fit(train_x, train_y)
		    self._report(grid_search.grid_scores_, self.search_parameter_best_score_num, logger)
		else:
		    logger.info('splited_key[%s] do train' % splited_key)
		    clf = self._get_model(animal, logger)
		    clf.fit(train_x, train_y, eval_metric=self.train_loss)

		    # store model info
		    model_dict[splited_key] = {
			'clf': clf,
			'model_infos': model_infos
		    }
		    joblib.dump(clf, '.'.join([self.model_filename, splited_key]))
		    self._dump_model_info(model_infos, logger)

		    # do validtaion
		    if self.do_validate:
			scores = cross_validation.cross_val_score(clf, train_x, train_y, pre_dispatch=1, scoring=self.validate_loss)
			print 'accrucy mean %0.2f +/- %0.2f' % (scores.mean(), scores.std()*2)
			logger.info('splited_key[%s] accrucy mean %0.2f +/- %0.2f' % (splited_key, scores.mean(), scores.std()*2))
	else:
	    logger.info('load trained model...')
	    for splited_key, splited_data in splited_data_dict.iteritems():
		clf = joblib.load('.'.join([self.model_filename, splited_key]))
		model_infos = self._load_model_info(splited_key)

		# store model info
		model_dict[splited_key] = {
		    'clf': clf,
		    'model_infos': model_infos
		}

	if self.do_test:
	    encoded_y = self._transfer_test_to_model(cleaned_test_data, model_dict, combine_data, external_data, logger)
	    self._ouput_result(encoded_y, self.submission_filename, logger)
