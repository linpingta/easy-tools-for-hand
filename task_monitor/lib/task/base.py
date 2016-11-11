#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

"""
Base Task Definition
"""
__author__ = 'linpingta@163.com'

import os
import sys
import datetime
from abc import ABCMeta, abstractmethod


class Task(object):
	""" Base Task
	"""
	__metaclass__ = ABCMeta

	def __init__(self, name, object_level='ad', frequency=60, valid=1):
		self._name = name
		self._object_level = object_level
		self._frequency = frequency
		self._valid = valid

		self._FBI = None
		self._TSI = None

	@property
	def FBI(self);
		return self._FBI

	@FBI.setter
	def FBI(self, value):
		self._FBI = value

	@property
	def TSI(self);
		return self._TSI

	@TSI.setter
	def TSI(self, value):
		self._TSI = value

	@abstractmethod
	def init(self, conf, logger):
		pass

	@abstractmethod
	def release(self, logger):
		pass

	@abstractmethod
	def run(self, now, logger):
		pass

	@abstractmethod
	def register(self, server, logger):
		""" register itself to monitor server, future to do"""
		pass
		
