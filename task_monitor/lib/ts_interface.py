#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

""" DB API"""
__author__ = 'linpingta@163.com'

import os
import sys
import logging
try:
	import ConfigParser
    import cPickle as pickle
except ImportError:
	import configparser as ConfigParser
    import pickle
import MySQLdb


class TSI(object):
	"""包装DB API的调用接口
	"""
	def __init__(self, conf):
		""" 保存db调用接口"""
		db_host = conf.get('db', 'host')
		db_port = conf.getint('db', 'port')
		db_user = conf.get('db', 'user')
		db_passwd = conf.get('db', 'passwd')
		db_name = conf.get('db', 'name')
		self.conn = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_passwd, db=self.db_name, port=self.db_port,charset='utf8')
		self.cur = self.conn.cursor()

	def release(self, logger):
		if self.conn:
			self.cur.close()
			self.conn.close()
