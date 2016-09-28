#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

''' Base Sender'''
__author__ = 'linpingta@163.com'


class BaseSender(object):
	''' basic sender for monitor result
	'''
	def __init__(self, conf, title):
		pass

	def send(self, ad_info_objects, now, logger):
		pass
