#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

""" Argument Define"""
__author__ = 'chutong'


import os
import sys
from abc import ABCMeta, abstractmethod


class Argument(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	@classmethod
	def get(cls, result_path, parent_ids, logger):
		pass


class EmptyArgument(Argument):
	""" Used for argument define
	"""
	@classmethod
	def get(cls, result_path, parent_ids, logger):
		return []


class TopAppArgument(Argument):
	""" Used for argument define
	"""
	@classmethod
	def get(cls, result_path, parent_ids, logger):
		try:
			parent_id = parent_ids[0]
			df = pd.read_csv(os.path.join(result_path, 'result_%d.csv' % parent_id))
			print df['application_id']
			application_ids = df['application_id'].tolist()
			application_id_str = ''
			for idx, application_id in enumerate(application_ids):
				application_id_str += str(application_id)
				if idx < len(application_ids) - 1:
					application_id_str += ','
			print application_id_str
			arguments = []
			arguments.append(application_id_str)
			return arguments
		except Exception as e:
			logger.exception(e)


