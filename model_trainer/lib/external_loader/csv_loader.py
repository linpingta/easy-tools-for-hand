#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' csv loader'''
__author__ = 'chutong'


import pandas as pd
import time


class TsCsvLoader(object):
    ''' CSV Loader 
    '''  
    def __init__(self):
        pass

    def load(self, filename, logger):
        try:
            return pd.read_csv(filename)
        except Exception as e:
            logger.exception(e)

    def dump(self, data, filename, logger, time_store=False):
        try:
            data.to_csv(filename)
            if time_store:
                postfix_time = time.strftime('%Y%m%d%H%M', time.localtime())
                postfix_filename = '.'.join([filename, str(postfix_time)])
                data.to_csv(postfix_filename)
	except Exception as e:
	    logger.exception(e)
