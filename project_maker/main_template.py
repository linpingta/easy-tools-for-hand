#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

""" Template Main Function"""
__author__ = 'linpingta@163.com'


import os
import sys
try:
	import ConfigParser
except:
	import configparser as ConfigParser
import logging


if __name__ == '__main__':

	try:
		basepath = os.path.abspath(sys.path[0])

		script_name = os.path.splitext(os.path.basename(__file__))[0]
		logging.basicConfig(filename=os.path.join(basepath, 'logs/' + script_name + '.log'), level=logging.DEBUG,
			format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
			datefmt = '%a, %d %b %Y %H:%M:%S'
			)
		logger = logging.getLogger('Base')
		confpath = os.path.join(basepath, 'conf/aam.conf')
		conf = ConfigParser.RawConfigParser()
		conf.read(confpath)

		example_word = """example:

			DESCRIBE YOUR EXAMPLE HERE
			python base.py -t argument1
		"""

		import argparse
		parser = argparse.ArgumentParser(prog='base', description='base template', epilog=example_word, formatter_class=argparse.RawDescriptionHelpFormatter)
		#add parameter if needed
		parser.add_argument('-t', '--template', help='argument description here', type=str)
		args = parser.parse_args()

		# main function
		print "Hello, World"

	except argparse.ArgumentTypeError as e:
		logger.exception(e)
	except Exception as e:
		logger.exception(e)
