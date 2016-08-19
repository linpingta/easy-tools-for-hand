#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

import sys
import time
import pyhs2


class HiveConnector(object):

	def __init__(self, host, port, db, auth, user, password): 
        self.host = host
        self.port = port
        self.db = db
		self.auth = auth
		self.user = user
		self.password = password

	def getConn(self):
		conn = pyhs2.connect(self.host, self.port, self.auth, self.user, self.password, self.db)
		return conn

