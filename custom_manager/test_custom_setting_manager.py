# -*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

__author__ = 'linpingta@163.com'

import os
import sys
import logging
import unittest

from custom_setting_manager import CustomSettingManager


class CustomSettingManagerTest(unittest.TestCase):
	"""
	Test CustomSettingManager
	"""
	basepath = os.path.abspath(os.getcwd())
	logging.basicConfig(filename=os.path.join(basepath, 'logs/test_custom_setting.log'), level=logging.INFO,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('TestCustomSettingManager')

	def test_load(self):
		basepath = self.basepath
		logger = self.logger

		filename = os.path.join(basepath, 'conf/custom_setting.xml')
		CustomSettingManager.load(filename, logger)
		self.assertIsNotNone(CustomSettingManager.custom_setting_dict)

		filename = os.path.join(basepath, 'conf/not_exist.xml')
		with self.assertRaises(IOError):
			CustomSettingManager.load(filename, logger)

	def test_get_user_in_custom_setting(self):
		basepath = self.basepath
		logger = self.logger
		
		filename = os.path.join(basepath, 'conf/custom_setting.xml')
		CustomSettingManager.load(filename, logger)

		# user not exist
		user_setting_dict = CustomSettingManager.get_user_in_custom_setting(1,'ABC', logger)
		self.assertIsNone(user_setting_dict)

		# user exist, status not exist
		user_setting_dict = CustomSettingManager.get_user_in_custom_setting(1234,'NOTEXIST', logger)
		self.assertIsNone(user_setting_dict)

		# user & status exist, check value
		user_setting_dict = CustomSettingManager.get_user_in_custom_setting(12345,'ExpStatus', logger)
		self.assertEqual(user_setting_dict['target'], '100')
		self.assertEqual(user_setting_dict['recent'], '150')


if __name__ == '__main__':
	unittest.main()
