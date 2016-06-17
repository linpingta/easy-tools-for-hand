#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

__author__ = 'chutong@domob.cn'

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
from task.fb_account_check_monitor import FbAccountCheckMonitor


if __name__ == '__main__':

    basepath = os.path.abspath(os.path.dirname(sys.path[0]))
    confpath = os.path.join(basepath, 'conf/task.conf')
    conf = ConfigParser.RawConfigParser()
    conf.read(confpath)

    logging.basicConfig(filename=os.path.join(basepath, 'logs/fb_account_check.log'), level=logging.DEBUG,
        format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
        datefmt = '%a, %d %b %Y %H:%M:%S'
        )
    logger = logging.getLogger('FbAccountCheck')

    email_sender = EmailSender(conf, 'fb_account_check')
    mt = FbAccountCheckMonitor(sender=email_sender)
    mt.init(conf, logger)
    try:
    	now = time.localtime()
        mt.run(now, logger)
    except Exception as e:
        logger.exception(e)
    finally:
        mt.release(logger)