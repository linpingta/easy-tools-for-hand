#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Base Sender"""
__author__ = 'linpingta@163.com'

from abc import ABCMeta, abstractmethod


class BaseSender(object):
	""" Basic sender for Monitor
	"""
	__metaclass__ = ABCMeta
	def __init__(self, conf, title="BaseSender"):
		self._title = title

	@property
	def title(self):
		return self._title

	@abstractmethod
	def send(self, logger):
		pass
