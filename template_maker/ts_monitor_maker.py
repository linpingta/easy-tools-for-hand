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


def split_filename(filename):
	paths = os.path.split(filename)
	return os.path.splitext(paths[-1])[0]


if __name__ == '__main__':

	try:
		basepath = os.path.abspath(sys.path[0])

		script_name = os.path.splitext(os.path.basename(__file__))[0]
		logging.basicConfig(filename=os.path.join(basepath, 'logs/' + script_name + '.log'), level=logging.DEBUG,
			format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
			datefmt = '%a, %d %b %Y %H:%M:%S'
			)
		logger = logging.getLogger('MonitorMaker')

		example_word = """example:

			python ts_monitor_maker.py -t monitor_template1.py,monitor_template2.py
			python ts_monitor_maker.py -t templates/monitor_template.py -c conf/marker.conf
			python ts_monitor_maker.py -t templates/monitor_template.py 
			python ts_monitor_maker.py -t monitor_template.py -c conf/marker.conf
			python ts_monitor_maker.py -t monitor_template
		"""

		import argparse
		parser = argparse.ArgumentParser(prog='monitor_maker', description='template maker', epilog=example_word, formatter_class=argparse.RawDescriptionHelpFormatter)
		parser.add_argument('-t', '--templates', help='template names to make, should be defined as section name in conf, and have related file in templates/', type=str)
		parser.add_argument('-c', '--confpath', help='configuration path for template detail info', type=str, default=os.path.join(basepath, 'conf/maker.conf'))
		args = parser.parse_args()
		if not args.templates:
			parser.print_help()
			logger.error('no template input from CLI')
		elif not args.confpath:
			parser.print_help()
			raise ValueError("no confpath input from CLI")
		else:
			conf = ConfigParser.RawConfigParser()
			conf.read(args.confpath)
			new_templates = []
			[ new_templates.append(split_filename(template.strip())) for template in args.templates.split(',') ]
			bm = MonitorMaker(new_templates)
			bm.init(conf, logger, script_name, basepath)
			bm.make(logger)
	except ValueError, e:
		logging.exception(e)
	except Exception,e:
		logging.exception(e)

