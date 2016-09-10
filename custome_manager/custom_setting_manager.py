# -*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

__author__ = 'linpingta@163.com'

import os,sys
import logging
import ConfigParser
import xmltodict


class CustomSettingManager(object):
	''' 负责用户特殊设置参数的加载
	'''
	custom_setting_dict = {}

	@classmethod
	def get_user_in_custom_setting(cls, my_user_id, status_name, logger):
		user_status_setting_dict = {}
		try:
			if not cls.custom_setting_dict:
				logger.warning('custom setting dict is empty')
			else:
				# check user first
				user = {}
				custom_users = cls.custom_setting_dict['custom_setting']['user']
				for custom_user in custom_users:
					if int(custom_user['@id']) == my_user_id:
						user = custom_user
						break

				# check status
				if user and (status_name in user):
					user_status_setting_dict = user[status_name]
			
		except Exception as e:
			logger.exception(e)
		finally:
			return user_status_setting_dict

	@classmethod
	def load(cls, filename, logger):
		''' 加载配置文件'''
		try:
			with open(filename, 'r') as fp_r:
				cls.custom_setting_dict = xmltodict.parse(fp_r.read())
			print cls.custom_setting_dict
		except Exception as e:
			logger.exception(e)
		

if __name__ == '__main__':

	# test CustomSettingManager
	basepath = os.path.abspath(os.getcwd())
	filename = os.path.join(basepath, 'conf/custom_setting.xml')

	logging.basicConfig(filename=os.path.join(basepath, 'logs/mock.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('CustomSettingManager')

	try:
		CustomSettingManager.load(filename, logger)
		user_setting_dict = CustomSettingManager.get_user_in_custom_setting(1,'ABC', logger)
		print user_setting_dict
		user_setting_dict = CustomSettingManager.get_user_in_custom_setting(1234,'ABC', logger)
		print user_setting_dict
		user_setting_dict = CustomSettingManager.get_user_in_custom_setting(12345,'ExpStatus', logger)
		print user_setting_dict
	except Exception, e:
		logger.exception(e)
