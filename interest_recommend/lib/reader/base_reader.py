#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Base Reader for local file"""

from abc import ABCMeta, abstractmethod


class BaseReader(object):
	""" Base Reader
	abstract method: read(filename, logger)
	"""
	__meta__ = ABCMeta

	def __init__(self, conf):
		pass

	@abstractmethod
	def read(self, filename, logger):
		pass

	@abstractmethod
	def dump(self, model, filename, logger):
		pass

