#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Base Cleaner"""
__author__ = 'chutong'


from abc import ABCMeta, abstractmethod


class TsCleaner(object):
	""" Abstract data cleaner
	"""
	__meta__ = ABCMeta

	@abstractmethod
	def clean(self, data, logger):
		pass

