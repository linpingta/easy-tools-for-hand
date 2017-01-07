#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Base Model Loader"""
__author__ = 'chutong'


from abc import ABCMeta, abstractmethod


class TsModelLoader(object):
	""" Abstract Model Loader 
	"""
	__meta__ = ABCMeta

	def __init__(self, model_conf):
		pass

	@abstractmethod
	def load_model(self, filename, logger):
		pass

	@abstractmethod
	def load_model_infos(self, model_name_dict, logger):
		pass

	@abstractmethod
	def dump_model(self, data, filename, logger, time_store=False):
		pass

	@abstractmethod
	def dump_model_infos(self, model_infos, model_info_filename_prefix, splited_key, logger, time_store=False):
		pass

	@abstractmethod
	def get_model(self, splited_key, logger):
		pass
