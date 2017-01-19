#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import pandas as pd
from base_reader import BaseReader


class DataFrameReader(BaseReader):
	""" read/dump df in pandas
	"""
	def read(self, filename, logger):
		return pd.read_csv(filename, encoding="utf-8")
	
	def dump(self, df, filename, logger):
		df.to_csv(filename, encoding="utf-8")
