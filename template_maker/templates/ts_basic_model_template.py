{% extends 'base_template.py' %}

{% block ext_import %}
import datetime
try:
    import cPickle as pickle
except:
    import pickle
import simplejson as json
import MySQLdb
import pandas as pd

from basic_model import BasicModel
from basic_model_manager import BasicModelManager, {{ model_capital_level }} 
{% endblock ext_import%}

{% block main %}
    try:
        {{model_capital_name}}(conf).run(logger)
    except Exception as e:
        logger.exception(e)
{% endblock main %}

{% block body %}
class {{ model_capital_name }}Model(BasicModel):
	''' {{ model_capital_name }} Model
	'''
	def __init__(self, conf):
		super({{ model_capital_name }}Model, self).__init__(conf)
	{% if model_store_name is defined %}
		self.{{ model_store_name }}_dict = {}
		self.{{ model_store_name }}_filename = conf.get('{{ model_name }}', '{{ model_store_name }}_filename')
	{% endif %}

	def init(self, now, logger):
		super({{ model_capital_name }}Model, self).init(now, logger)
		self.ZI.init_db(self.conf, logger)

	def load(self, now, logger):
	{% if model_store_name is defined %}
		with open(self.{{ model_store_name }}_filename, 'rb') as fp_r_pickle:
			self.{{ model_store_name}}_dict = pickle.load(fp_r_pickle)
	{% else %}
		pass
	{% endif %}
	def dump(self, now, logger):
		if self.{{ model_store_name }}_dict:
			with open(self.{{ model_store_name }}_filename, 'wb') as fp_w_pickle:
				pickle.dump(self.{{ model_store_name }}_dict, fp_w_pickle)

	def release(self, logger):
		super({{ model_capital_name }}Model, self).release(logger)
		self.ZI.release_db(logger)

{% if model_level == 'account' %}
	def run(self, account_id, now, logger):
{% elif model_level == 'campaign' %}
	def run(self, account_id, campaign, now, logger):
{% endif %}
		try:
			pass
		except Exception as e:
			logger.exception(e)


class {{ model_capital_name }}Manager(BasicModelManager, {{ model_capital_level }}):
	''' 离线模型管理
	'''
	def __init__(self, conf):
		super({{ model_capital_name }}Manager, self).__init__(conf)

		self._call_wait_hours = conf.getfloat('{{model_name}}', 'call_wait_hours')
		self.logname_prefix = conf.get('{{model_name}}', 'logname_prefix')
		self.conf = conf

	def _create_model(self, logger):
		''' Model初始化处理'''
		self.{{ model_name }}_model = {{ model_capital_name }}Model(self.conf)

	def _init_model(self, now, logger):
		''' Model初始化处理'''
		# 加载模型设置
		self.{{ model_name }}_model.init(now, logger)

	def _store_model(self, now, logger):
		''' Model保存'''
		self.{{ model_name }}_model.dump(now, logger)

	def _release_model(self, logger):
		''' Model释放处理'''
		self.{{ model_name }}_model.release(logger)

{% if model_level == 'account' %}
	def _run(self, account_id, now, logger):
		try:
			logger.debug('read account_id %d' % account_id)
			self.{{ model_name }}_model.run(account_id, now, logger)

		except Exception, e:
			logger.exception(e)

{% elif model_level == 'campaign' %}
	def _run(self, account_id, campaign, now, logger):
		''' 针对每个Campaign的调用'''
		try:
			logger.debug('read auto cpid %d status %d paused %d' % (campaign.id, campaign.status, campaign.paused))
			self.{{ model_name }}_model.run(account_id, campaign, now, logger)

		except Exception, e:
			logger.exception(e)
{% endif %}

{% endblock body %}
