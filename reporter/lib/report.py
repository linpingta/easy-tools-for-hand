#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :


''' Element With Business Logic'''
__author__ = 'chutong'


import os
import sys
import logging
try:
	import configparser as ConfigParser
except:
	import ConfigParser
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
		plt_handlers = []
		for component in self._components:
			component.handler = self._handler
			plt_handler = component.render(logger)
			if not plt_handler:
				logger.error("component %s not plot" % component.name)
			else:
				plt_handlers.append(plt_handler)
		return plt_handlers
				


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

	print type(pdf_handler)

	# add content
	data_filename = "bid1"
	content1 = Content(conf, data_filename)
	query = DataQueryFactory.build('df', os.path.join(basepath, "data/%s.csv" % data_filename))
	renderer = RenderFactory.build('line', data_filename)
	content1.set_data_query(query)
	content1.set_renderer(renderer)
	content1.query_df(logger)
	print content1.df_attributes
	print type(renderer)
	content1.dimensions = ['dt']
	content1.metrics = ['avg_relevance_score']
	reporter.add_component(content1)

	## add content
	#data_filename = "bid2"
	#content2 = Content(conf, data_filename)
	#query = DataQueryFactory.build('df', os.path.join(basepath, "data/%s.csv" % data_filename))
	##query = DataQueryFactory.build('task', 200, conf)
	#renderer = RenderFactory.build('line')
	#content2.set_data_query(query)
	#content2.set_renderer(renderer)
	#content2.query_df(logger)
	#print content2.df_attributes
	#content2.dimenions = []
	#content2.metrics = []
	#reporter.add_component(content2)

	plt_handlers = reporter.render(logger)
	for plt_handler in plt_handlers:
		print 'abc'
		print type(plt_handler)
		plt_handler.savefig(pdf_handler, format="pdf")
		plt_handler.close()

	#d = pdf_handler.infodict()
	#d['Title'] = 'Multipage PDF Example'
	#d['Author'] = u'Chu Tong'
	#d['Subject'] = 'How to create a multipage pdf file and set its metadata'
	#d['Keywords'] = 'PdfPages multipage keywords author title subject'
	#d['CreationDate'] = datetime.datetime(2009, 11, 13)
	#d['ModDate'] = datetime.datetime.today()
