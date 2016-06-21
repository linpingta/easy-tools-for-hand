#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

__author__ = '{{author}}@{{mailbox}}'
import os, sys
import time
try:
	import ConfigParser
except:
	import configparser as ConfigParser
import logging
{% block ext_import %}
{% endblock ext_import %}

if __name__ == '__main__':

    basepath = os.path.abspath(os.path.dirname(sys.path[0]))
    confpath = os.path.join(basepath, 'conf/{{conf_name}}.conf')
    conf = ConfigParser.RawConfigParser()
    conf.read(confpath)

    logging.basicConfig(filename=os.path.join(basepath, 'logs/{{model_name}}.log'), level=logging.DEBUG,
        format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
        datefmt = '%a, %d %b %Y %H:%M:%S'
        )
    logger = logging.getLogger('{{model_capital_name}}')

{% block main %}
{% endblock main %}
