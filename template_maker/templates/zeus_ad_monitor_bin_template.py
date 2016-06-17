#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

__author__ = '{{author}}@{{mailbox}}'

import os, sys
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
sys.path.append(os.path.join(basepath, 'lib'))
import time
try:
	import ConfigParser
except:
	import configparser as ConfigParser
import logging

from sender.email_sender import EmailSender
from task.{{ lib_model_name }} import {{ lib_model_capital_name }}


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

    email_sender = EmailSender(conf, '{{model_name}}')
    mt = {{ lib_model_capital_name }}(sender=email_sender)
    mt.init(conf, logger)
    try:
    	now = time.localtime()
        mt.run(now, logger)
    except Exception as e:
        logger.exception(e)
    finally:
        mt.release(logger)
