#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' base model loader'''
__author__ = 'chutong'


class TsModelLoader(object):
    ''' Base Model Loader 
    '''  
	def __init__(self):
		pass

	def load_model(self, filename, logger):
		pass

	def load_model_infos(self, model_name_dict, logger):
		pass

	def dump_model(self, data, filename, logger, time_store=False):
		pass

	def dump_model_infos(self, model_infos, model_filename_dict, logger, time_store=False):
		pass

