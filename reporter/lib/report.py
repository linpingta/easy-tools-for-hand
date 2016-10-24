#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :


''' Element With Business Logic'''
__author__ = 'chutong'


import os
import sys
import datetime
import logging
try:
	import configparser as ConfigParser
except:
	import ConfigParser
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

from base import Composite
from content import Content
from data_query import DataQueryFactory
from render import RenderFactory


class PdfReport(Composite):
	'''
	Combine contents into one report
	'''
	def __init__(self):
		self._handler = None
		self._components = []

	@property
	def handler(self):
		return self._handler

	@handler.setter
	def handler(self, handler):
		self._handler = handler

	def add_component(self, component):
		if isinstance(component, PdfReport):
			raise TypeError("forbid to add PdfReport to another PdfReport")
		self._components.append(component)

	def render(self, logger):
		for component in self._components:
			logger.info('report render content[%s]' % component.name)
			component.handler = self._handler
			component.render(logger)



if __name__ == '__main__':
	basepath = os.path.abspath(os.path.dirname(sys.path[0]))
	confpath = os.path.join(basepath, 'conf/report.conf')
	conf = ConfigParser.RawConfigParser()
	conf.read(confpath)
	logging.basicConfig(filename=os.path.join(basepath, 'logs/report.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('Reporter')

	reporter = PdfReport()
	with PdfPages(os.path.join(basepath, "output/test.pdf")) as pdf_handler:
		reporter.handler = pdf_handler

		# add content
		data_filename = "bid1"
		content1 = Content(conf, data_filename)
		#query = DataQueryFactory.build('task', 200, conf)
		query = DataQueryFactory.build('df', os.path.join(basepath, "data/%s.csv" % data_filename))
		renderer = RenderFactory.build('line')
		content1.set_data_query(query)
		content1.set_renderer(renderer)
		content1.query_df(logger)
		logger.info('content[%s] has df attributes %s' % (content1.name, str(content1.df_attributes)))
		content1.dimensions = ['dt']
		content1.metrics = ['avg_relevance_score']
		reporter.add_component(content1)

		# add content
		data_filename = "bid2"
		content2 = Content(conf, data_filename)
		query = DataQueryFactory.build('df', os.path.join(basepath, "data/%s.csv" % data_filename))
		renderer = RenderFactory.build('line')
		content2.set_data_query(query)
		content2.set_renderer(renderer)
		content2.query_df(logger)
		logger.info('content[%s] has df attributes %s' % (content2.name, str(content2.df_attributes)))
		content2.dimensions = ['image_url']
		content2.metrics = ['avg_relevance_score']
		reporter.add_component(content2)

		reporter.render(logger)

		d = pdf_handler.infodict()
		d['Title'] = conf.get('pdf_info', 'title')
		d['Author'] = conf.get('pdf_info', 'author')
		d['Subject'] = conf.get('pdf_info', 'subject')
		d['Keywords'] = conf.get('pdf_info', 'keywords')
		d['CreationDate'] = datetime.datetime.now()
