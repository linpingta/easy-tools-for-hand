#!/usr/bin/env python
#-*- coding: utf-8 -*-
# vim: set bg=dark noet sw=4 ts=4 fdm=indent : 

''' App Crawler'''
__author__='linpingta@163.com'

import os,sys
import logging
import ConfigParser

import re
import requests


class AppCrawler(object):
	''' App Info Fetcher, 
	maybe not crawler, but used for itunes store or google play store info fetch
	'''
	def __init__(self, conf):
		# app_url list
		self.app_urls = []
		# app_id as key, app_info (list) as value
		self.app_info_dict = {}

		self.country = conf.get('app_crawler','country')
		self.lang = conf.get('app_crawler','lang')

		self.requests = requests.Session()

	def _extract_unique_id(self, app_url, logger):
		return ''

	def _request(self, app_unique_id, logger):
		return []

	def load_file(self, app_url_file, logger):
		with open(app_url_file, 'r') as fp_r:
			while 1:
				line = fp_r.readline()
				line = line.strip()
				if not line:
					break
				self.app_urls.append(line)

	def save_file(self, app_url_file_output, logger):
		with open(app_url_file_output, 'w') as fp_w:
			for app_info in self.app_info_dict.values():
				t = []
				[ t.append(str(item)) for item in app_info ]
				t_s = ','.join(t)
				fp_w.write("%s" % t_s)

	def run(self, logger):
		for app_url in self.app_urls:
			logger.info('%s : %s fetch app_info' % (self.__class__.__name__, app_url))
			app_unique_id = self._extract_unique_id(app_url, logger)
			if not app_unique_id:
				logger.warning('no info extracted from app_url %s' % app_url)
			else:
				app_info = self._request(app_unique_id, logger)
				self.app_info_dict[app_unique_id] = app_info


class AndroidAppCrawler(AppCrawler):
	''' Android Info
	'''
	def __init__(self, conf):
		self.prefix_url = 'https://data.42matters.com/api/v2.0/android/apps/lookup.json'
		self.android_access_token = conf.get('app_crawler','android_access_token')

		super(AndroidAppCrawler, self).__init__(conf)

	def _extract_unique_id(self, app_url, logger):
		info = re.findall('id=(.*)', app_url, 0)
		return info[0] if info else ''

	def _request(self, app_unique_id, logger):

		method = 'GET'
		path = "/".join((self.prefix_url,
			'lookup',
		))
		params = {'p': app_unique_id,
			'access_token': self.access_token
		}
		response = self.requests.request(
			method,
			path,
			params=params
		)


class IosAppCrawler(AppCrawler):
	''' Ios Info
	'''
	def __init__(self, conf):
		self.prefix_url = 'https://itunes.apple.com'
		super(IosAppCrawler, self).__init__(conf)

	def _extract_unique_id(self, app_url, logger):
		info = re.findall('id(.*)', app_url, 0)
		return info[0] if info else ''

	def _request(self, app_unique_id, logger):

		method = 'GET'
		path = "/".join((self.prefix_url,
			'lookup',
		))
		params = {'id': app_unique_id}
		response = self.requests.request(
			method,
			path,
			params=params
		)


if __name__ == '__main__':

	basepath = os.path.abspath(os.path.dirname(sys.path[0]))
	confpath = os.path.join(basepath, 'conf/app_crawler.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)

	logging.basicConfig(filename=os.path.join(basepath, 'logs/app_crawler.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('AdManager')

	try:
		# android crawl
		app_url_file = 'data/android_urls'
		app_url_file_output = 'data/android_urls_output'
		android_crawler = AndroidAppCrawler(conf)
		android_crawler.load_file(app_url_file, logger)
		android_crawler.run(logger)
		android_crawler.save_file(app_url_file_output, logger)
	except Exception,e:
		logging.exception(e)
