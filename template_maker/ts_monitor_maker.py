#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import sys, os
try:
	import ConfigParser
except:
	import configparser as ConfigParser
import logging

from base_maker import BaseMaker


class MonitorMaker(BaseMaker):
	''' Template Monitor Maker
	'''
	def _generate(self, template_params_dict):
		generated_dict = {}
		if 'model_name' in template_params_dict:
			model_name = template_params_dict['model_name']
			model_part_name_group = model_name.split('_')
			model_capital_name = ''
			for model_part_name in model_part_name_group:
				model_capital_name += model_part_name.capitalize()
			generated_dict['model_capital_name'] = model_capital_name
		if 'lib_model_name' in template_params_dict:
			model_name = template_params_dict['lib_model_name']
			model_part_name_group = model_name.split('_')
			model_capital_name = ''
			for model_part_name in model_part_name_group:
				model_capital_name += model_part_name.capitalize()
			generated_dict['lib_model_capital_name'] = model_capital_name
		return generated_dict


if __name__ == '__main__':

	basepath = os.path.abspath(sys.path[0])

	script_name = os.path.splitext(os.path.basename(__file__))[0]
	logging.basicConfig(filename=os.path.join(basepath, 'logs/' + script_name + '.log'), level=logging.DEBUG,
		format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
		datefmt = '%a, %d %b %Y %H:%M:%S'
		)
	logger = logging.getLogger('MonitorMaker')

	try:
		import argparse
		parser = argparse.ArgumentParser(prog='monitor_maker', description='template maker')
		parser.add_argument('-t', '--templates', help='template names to make, should be defined as section name in conf, and have related file in templates/', type=str)
		parser.add_argument('-c', '--confpath', help='configuration path for template detail info', type=str, default=os.path.join(basepath, 'conf/maker.conf'))
		args = parser.parse_args()
		if not args.templates:
			logger.error('no template input from CLI')
		else:
			conf = ConfigParser.RawConfigParser()
			conf.read(args.confpath)
			templates = args.templates.split(',')
			bm = MonitorMaker(templates)
			bm.init(conf, logger, script_name, basepath)
			bm.make(logger)
	except Exception,e:
		logging.exception(e)

