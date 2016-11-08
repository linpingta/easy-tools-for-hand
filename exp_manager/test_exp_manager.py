#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

__author__ = 'linpingta@163.com'

import os
import sys
import logging
try:
	import ConfigParser
	import xml.etree.cElementTree as ET
except ImportError:
	import configparser as ConfigParser
	import xml.etree.ElementTree as ET
import unittest

from exp_manager import ExpManager


class ExpManagerTest(unittest.TestCase):
	def setUp(self):
		logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
			format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		)
		basepath = os.path.abspath(os.getcwd())
		self._input_filename = os.path.join(basepath, 'conf/test_exp.xml')

	def test_load_from_file(self):
		logger = logging.getLogger(__name__)
		ExpManager.load(self._input_filename, logger)
		self.assertEqual(ExpManager.strategy_info_dict["Mock"].id, 101)

		wrong_filename = 'not_exist.xml'
		with self.assertRaises(IOError):
			ExpManager.load(wrong_filename, logger)

	def test_has_user(self):
		logger = logging.getLogger(__name__)
		ExpManager.load(self._input_filename, logger)
		with ExpManager("Mock") as (exp, logger):
			from collections import OrderedDict
			user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
			self.assertTrue(exp.has_user(user_info))
			user_info = OrderedDict(user_id=1, account_id=123, campaign_id=12345)
			self.assertFalse(exp.has_user(user_info))

		with ExpManager("Mock2") as (exp, logger):
			from collections import OrderedDict
			user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
			self.assertTrue(exp.has_user(user_info))
			user_info = OrderedDict(user_id=1, account_id=123, campaign_id=12345)
			self.assertFalse(exp.has_user(user_info))

		with ExpManager("Mock3") as (exp, logger):
			from collections import OrderedDict
			user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
			self.assertTrue(exp.has_user(user_info))
			user_info = OrderedDict(user_id=1, account_id=111, campaign_id=1234)
			self.assertFalse(exp.has_user(user_info))

		with ExpManager("Mock4") as (exp, logger):
			from collections import OrderedDict
			user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
			self.assertTrue(exp.has_user(user_info))
			user_info = OrderedDict(user_id=2, account_id=123, campaign_id=1234)
			self.assertFalse(exp.has_user(user_info))


if __name__ == '__main__':
	unittest.main()
		

