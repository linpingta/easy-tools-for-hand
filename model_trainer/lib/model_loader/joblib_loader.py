#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' joblib loader'''
__author__ = 'chutong'


import time
from sklearn.externals import joblib


class TsJoblibModelLoader(object):
	''' Joblib Model Loader
	'''  
	def __init__(self):
		pass

	def load_model(self, filename, logger):
		return joblib.load(filename)

	def load_model_infos(self, model_names, model_info_filename_prefix, splited_key, logger):
		model_infos = {}
		for model_name in model_names:
			model_filename = os.path.join(model_info_filename_prefix, '.'.join([model_name, splited_key]))
			model_info = joblib.load(model_filename)
			model_infos[model_name] = model_info
		return model_infos

	def dump_model(self, data, filename, logger, time_store=False):
		joiblib.dump(data, filename)

		if time_store:
			postfix_time = time.strftime('%Y%m%d%H%M', time.localtime())
			postfix_filename = '.'.join([filename, str(postfix_time)])
			joiblib.dump(data, postfix_filename)

	def dump_model_infos(self, model_infos, model_info_filename_prefix, splited_key, logger, time_store=False):
		for model_name, model_info in model_infos.iteritems():
			model_filename = os.path.join(model_info_filename_prefix, '.'.join([model_name, splited_key]))
			joblib.dump(model_info, model_filename)

			if time_store:
				postfix_time = time.strftime('%Y%m%d%H%M', time.localtime())
				postfix_filename = '.'.join([model_filename, str(postfix_time)])
				joiblib.dump(model_info, postfix_filename)
