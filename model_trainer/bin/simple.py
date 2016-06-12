#-*- coding: utf-8 -*-
''' simple model caller example'''
__author__ = 'chutong'

import sys, os
import logging
import time, datetime
try:
    import ConfigParser
except:
    import configparser as ConfigParser
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
libpath = os.path.join(basepath, 'lib')
sys.argv.append(libpath)
from base_model import TsModel


if __name__ == '__main__':
    basepath = os.path.abspath(os.path.dirname(sys.path[0]))
    confpath = os.path.join(basepath, 'conf/simple.conf')
    conf = ConfigParser.RawConfigParser()
    conf.read(confpath)

    logging.basicConfig(filename=os.path.join(basepath, 'logs/simple.log'), level=logging.DEBUG,
        format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
        datefmt = '%a, %d %b %Y %H:%M:%S'
        )
    logger = logging.getLogger('simple')

    now = time.localtime()
    # use your model to substitue this, if you need
    TsModel(conf).run(now, logger)
    #TsRandomForestClassfier(conf).run(now, logger)
