#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

''' MOCK API'''
__author__ = 'linpingta@163.com'

import os, sys
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
sys.path.append(os.path.join(basepath, 'lib'))
import logging
import ConfigParser
import argparse
import time
import datetime
try:
    import cPickle as pickle
except:
    import pickle
import MySQLdb

from functools import partial
import copy
import simplejson as json


class TSI(object):
	''' 包装ts db API的调用接口'''
	def __init__(self):
		''' 保存db调用接口'''
		pass

