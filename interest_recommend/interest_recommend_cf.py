#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Interest Recommend Model"""
__author__ = 'chutong'

import os
import sys
import pandas as pd
import numpy as np
import argparse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances
from scipy import sparse

from base_model import BaseModel, main


class InterestRecommender(BaseModel):
	""" Recommend interest based on user input
	"""
	def __init__(self, basepath, conf):
		super(InterestRecommender, self).__init__(basepath, conf)	
		self._interests = []

	def _preprocess_data(self, df, logger):
		return df

		interest_df = []
		for row in enumerate(df.iterrows()):
			fb_ad_id = row[1]['fb_ad_id']
			interest_name = row[1]['interests_names']
			interests = interest_name.split(':')
			for interest in interests:
				t = (interest, fb_ad_id)
				interest_df.append(t)
		interest_df = pd.DataFrame(interest_df, columns=["fb_ad_id", "interest"])
		return interest_df

	def _postprocess_data(self, df, logger):
		interest_df = []
		for idx, row in enumerate(df.iterrows()):
			fb_ad_id = row[1]['fb_ad_id']
			interest_name = row[1]['interests_names']
			interests = interest_name.split(':')
			for interest in interests:
				interest = interest.replace('"', '').replace('[', '').replace(']', '')
				interest = interest.strip()
				t = (interest, fb_ad_id)
				interest_df.append(t)
		interest_df = pd.DataFrame(interest_df, columns=["interest", "fb_ad_id"])
		return interest_df

	def _fetch_data(self, now, logger):
		dimensions = ["fb_ad_id", "interests_names"]
		metrics = ["spend"]
		filters = [
			'interests_names != ""',
		]
		having = [
			'spend > 100',
		]
		return self._make_query(dimensions, metrics, filters, having, [], 0, now, self._start_dt, self._end_dt, logger)

	def _get_train_model(self, df, logger):
		df = self._postprocess_data(df, logger)

		interest_names = df['interest'].unique().tolist()
		fb_ad_ids = df['fb_ad_id'].unique().tolist()

		arr = []
		for idx, interest_name in enumerate(interest_names):
			t = np.zeros(len(fb_ad_ids))
			related_ad_ids = df[df['interest'] == interest_name]['fb_ad_id'].tolist()
			for related_ad_id in related_ad_ids:
				t[fb_ad_ids.index(related_ad_id)] = 1
			arr.append(t)

		arr = np.array(arr)
		dist_arr = 1 - pairwise_distances(arr, metric="cosine")
		return {'similar_arr':dist_arr, 'interest_names': interest_names}

	def _test(self, model, logger):

		dist_arr = model['similar_arr']
		interest_names = model['interest_names']

		for input_interest in self._interests:
			if input_interest not in interest_names:
				print "%s not exist" % input_interest
				return
			input_interest_idx = interest_names.index(input_interest)
			sub_arr = dist_arr[input_interest_idx]
			sorted_arr_index = np.argsort(sub_arr)
			max_similar_num = self._max_interest_num if len(sub_arr) > self._max_interest_num else len(sub_arr)
			
			idx_list = list(sorted_arr_index[-max_similar_num:])
			print input_interest
			for idx in idx_list:
				if interest_names[idx] == input_interest:
					continue
				print interest_names[idx], sub_arr[idx]

	def init(self, args, logger):
		super(InterestRecommender, self).init(args, logger)

		interests = args.interests.split(",")
		[ self._interests.append(interest.strip()) for interest in interests  if interest != "" ]
		self._max_interest_num = args.max_interest_num
		

def _extend_parse(parser):
	parser.add_argument("--interests", help="user input interests, split by comma", default="", type=str)
	parser.add_argument("--max_interest_num", help="max related interests num", default=10, type=int)


if __name__ == '__main__':

	main("interest_recommender", InterestRecommender, _extend_parse)
