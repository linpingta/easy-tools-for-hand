#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
''' shelter problem common operation'''
__author__ = 'chutong'


from base_model import TsModel
import xgboost as xgb
import numpy as np
import pandas as pd
import re
import time
from sklearn.feature_extraction import DictVectorizer as DV
from sklearn.preprocessing import LabelEncoder


class ShelterCommonModel(TsModel):
	''' Shelter Common Problem
	'''
	def __init__(self, conf):
		super(ShelterCommonModel, self).__init__(conf) 

	def _clean_data(self, data, logger):
		return data

	def _transfer_breed_input(self, origin_breed, logger):
		new_breed = []
		for breed in origin_breed:
			tmp_breed = breed.replace(' Mix', '')
			new_breed.extend(tmp_breed.split('/'))
			#part_breeds = breed.split(' Mi')
			#for part_breed in part_breeds:
			#	new_breed.extend(part_breed.split('/'))
		return new_breed

	def _transfer_color_input(self, origin_color, logger):
		new_color = []
		for color in origin_color:
			new_color.extend(color.split(' '))
		return new_color

	def _generate_combine_data(self, cleaned_train_data, cleaned_test_data, logger):

		train_breed = cleaned_train_data['Breed'].unique()
		test_breed = cleaned_test_data['Breed'].unique()
		new_train_breed = self._transfer_breed_input(train_breed, logger)
		new_test_breed = self._transfer_breed_input(test_breed, logger)
		total_breed = list(set(new_train_breed) | set(new_test_breed))

		train_color = cleaned_train_data['Color'].unique()
		test_color = cleaned_test_data['Color'].unique()
		new_train_color = self._transfer_color_input(train_color, logger)
		new_test_color = self._transfer_color_input(test_color, logger)
		total_color = list(set(new_train_color) | set(new_test_color))

		return (total_breed, total_color)

	def _split_data(self, data, logger):
		return {'all': data}

	def _transfer_age_info(self, age):
		if (not age) or (age is np.nan):
		#	return 'age0'
			return 0

		age_in_day = 1
		year = re.search('([0-9]*) year', age)
		if year:
			year_num = year.group(1)
			age_in_day = 365 * int(year_num)
		month = re.search('([0-9]*) month', age)
		if month:
			month_num = month.group(1)
			age_in_day = 30 * int(month_num)
		week = re.search('([0-9]*) week', age)
		if week:
			week_num = week.group(1)
			age_in_day = 7 * int(week_num)
		day = re.search('([0-9]*) day', age)
		if day:
			day_num = day.group(1)
			age_in_day = int(day_num) 
		##return 'age' + str(age_in_day)

		## manual split age
		#age_list = [0, 30, 90, 365 * 0.5, 365, 365 * 2, 365 * 5, 365 * 10]
		#for idx, start_age in enumerate(age_list):
		#	if age_in_day < start_age:
		#		return 'age' + str(idx + 1)
		#return 'age' + str(len(age_list) + 1)
		return age_in_day

	def _transfer_year_info(self, animal_time):
		s = time.strptime(animal_time, '%Y-%m-%d %H:%M:%S')
		return s.tm_year

	def _transfer_month_info(self, animal_time):
		s = time.strptime(animal_time, '%Y-%m-%d %H:%M:%S')
		return s.tm_mon

	def _transfer_weekday_info(self, animal_time):
		s = time.strptime(animal_time, '%Y-%m-%d %H:%M:%S')
		return s.tm_wday
		#if 5 <= s.tm_wday <= 6:
		#	return 'weekend'
		#else:
		#	return 'weekday'

	def _transfer_hour_info(self, animal_time):
		s = time.strptime(animal_time, '%Y-%m-%d %H:%M:%S')
		return s.tm_hour
		#if 5 < s.tm_hour < 11:
		#	return 'hour1'
		#elif 10 < s.tm_hour < 16:
		#	return 'hour2'
		#elif 15 < s.tm_hour < 20:
		#	return 'hour3'
		#else:
		#	return 'hour4'

	def _transfer_unix_datetime_info(self, animal_time):
		s = time.strptime(animal_time, '%Y-%m-%d %H:%M:%S')
		return int(time.mktime(s))

	def _transfer_name_len(self, name):
		#return True if name else False
		#return 'HasName' if name else 'HasNotName'
		#if name is np.nan:
		#	return False
		#else:
		#	return True
		return len(name) if name is not np.nan else 0

	def _transfer_sex_info(self, sex):
		if sex is np.nan:
			return 'Unknown'

		choices = ['Female', 'Male']
		for choice in choices:
			if choice in sex:
				return choice
		return 'Unknown'

	def _transfer_intact_info(self, sex):
		if sex is np.nan:
			return 'Unknown'
		choices = ['Intact', 'Neutered', 'Spayed']
		for choice in choices:
			if choice in sex:
				return choice
		return 'Unknown'

	def _transfer_breed_mix_info(self, breed):
		#return 'Mix' if ('Mix' in breed or '/' in breed) else 'UnMix'
		#return 'Mix' if 'Mix' in breed else 'UnMix'
		return len(breed.split('/')) - 1

	def _transfer_color_count_info(self, color):
		return len(color.split('/'))

	def _transfer_breed_type_info(self, breed, breed_type):
		#if breed_type in breed:
		#	if '/' in breed:
		#		return 0.5
		#	else:
		#		return 1
		#else:
		#	return 0
		return 1 if  breed_type in breed else 0

	def _transfer_color_type_info(self, color, color_type):
		#if color_type in color:
		#	if ' ' in color:
		#		return 0.5
		#	else:
		#		return 1
		#else:
		#	return 0
		return 1 if color_type in color else 0

	def _encode_y(self, y, logger):
		le_y = LabelEncoder()
		le_y.fit(y)
		encode_y = le_y.transform(y)
		return (encode_y, le_y)

	def _get_param_grid(self, splited_key, logger):
		param_grid = {
			'max_depth':[3,10], 
			'n_estimators':[10, 100]
		}
		return param_grid

	def _fit_transform(self, df, logger):
		output = df.copy()
		col_le_dict = {}
		for colname, col in output.iteritems():
			le = LabelEncoder()
			output[colname] = le.fit_transform(col)
			col_le_dict[colname] = le
		return (output, col_le_dict)

	def _fit(self, df, logger):
		col_le_dict = {}
		for colname, col in df.iteritems():
			le = LabelEncoder()
			le.fit(col)
			col_le_dict[colname] = le
		return col_le_dict

	def _transform(self, df, col_le_dict, logger):
		output = df.copy()
		for colname, col in output.iteritems():
			le = col_le_dict[colname]
			output[colname] = le.transform(col)
			col_le_dict[colname] = le
		return output

	def _encode_feature(self, splited_key, train_data, test_data, external_data, logger):
		""" feature transfer and encoding """

		# encode y
		logger.debug('splited_key[%s] encode y' % splited_key)
		(train_y, le_y) = self._encode_y(train_data['OutcomeType'].values, logger)

		(total_breed, total_color) = self._generate_combine_data(train_data, test_data, logger)

		test_data.rename(columns={'ID':'AnimalID'}, inplace=True)
		feature_columns = test_data.columns
		feature_train_data = train_data[feature_columns]
		feature_train_data.loc[:, 'data_type'] = 'train'
		feature_test_data = test_data[feature_columns]
		feature_test_data.loc[:, 'data_type'] = 'test'
		logger.debug('feature_train_data columns %s' % str(feature_train_data.columns))
		logger.debug('feature_test_data columns %s' % str(feature_test_data.columns))

		data = pd.concat([feature_train_data, feature_test_data])
		logger.debug('feature_train_data shape %s' % str(feature_train_data.shape))
		logger.debug('feature_test_data shape %s' % str(feature_test_data.shape))
		logger.debug('data shape %s' % str(data.shape))

		logger.debug('splited_key[%s] encode x' % splited_key)
		data['EncodeYear'] = data['DateTime'].apply(self._transfer_year_info)
		data['EncodeMonth'] = data['DateTime'].apply(self._transfer_month_info)
		data['EncodeWeekday'] = data['DateTime'].apply(self._transfer_weekday_info)
		data['EncodeHour'] = data['DateTime'].apply(self._transfer_hour_info)
		data['UnixDateTime'] = data['DateTime'].apply(self._transfer_unix_datetime_info)

		data['EncodeAgeuponOutcome'] = data['AgeuponOutcome'].apply(self._transfer_age_info)

		data = data[data['SexuponOutcome'] != '']

		data['NameLen'] = data['Name'].apply(self._transfer_name_len)

		if self._encode_type == 'dv':
			for breed_type in total_breed:
				data[breed_type] = data['Breed'].apply(self._transfer_breed_type_info, args=(breed_type,))
			for color_type in total_color:
				data[color_type] = data['Color'].apply(self._transfer_color_type_info, args=(color_type,))
		data['BreedMix'] = data['Breed'].apply(self._transfer_breed_mix_info)
		data['ColorCount'] = data['Color'].apply(self._transfer_color_count_info)
		data['Sex'] = data['SexuponOutcome'].apply(self._transfer_sex_info)
		data['Intact'] = data['SexuponOutcome'].apply(self._transfer_intact_info)

		logger.debug('transfer feature_train_data shape %s' % str(feature_train_data.shape))
		logger.debug('transfer feature_test_data shape %s' % str(feature_test_data.shape))

		drop_list = ['AnimalID', 'Name', 'DateTime', 'AgeuponOutcome', 'SexuponOutcome']
		data = data.drop(drop_list, 1)
		transfer_train_data = data[data['data_type'] == 'train']
		transfer_test_data = data[data['data_type'] == 'test']
		type_drop_list = ['data_type']
		transfer_train_data = transfer_train_data.drop(type_drop_list, 1)
		transfer_test_data = transfer_test_data.drop(type_drop_list, 1)
		data = data.drop(type_drop_list, 1)

		if self._encode_type == 'dv': # one-hot encoder
			x_all = data.T.to_dict().values()
			vectorizer_x = DV(sparse=False)
			vectorizer_x.fit(x_all)

			x1 = transfer_train_data.T.to_dict().values()
			train_x = pd.DataFrame(vectorizer_x.fit_transform(x1))
			x2 = transfer_test_data.T.to_dict().values()
			test_x = pd.DataFrame(vectorizer_x.transform(x2))

			model_infos = {'vectorizer_x':vectorizer_x, 'le_y':le_y}

		elif self._encode_type == 'label': # label encode
			col_le_dict = self._fit(data, logger)
			train_x = self._transform(transfer_train_data, col_le_dict, logger)
			test_x = self._transform(transfer_test_data, col_le_dict, logger)
			model_infos = {'col_le_dict':col_le_dict, 'le_y':le_y}
		else:
			raise ValueError("encode_type not valid, [label, dv] supported")

		logger.debug('splited_key[%s] train_x shape %s' % (splited_key, str(train_x.shape)))
		logger.debug('splited_key[%s] train_y shape %s' % (splited_key, str(train_y.shape)))
		logger.debug('splited_key[%s] test_x shape %s' % (splited_key, str(test_x.shape)))

		return (train_x, train_y, test_x, model_infos)

	def _train(self, clf, train_x, train_y, splited_key, logger):
		logger.info('splited_key[%s] do training' % splited_key)
		# xgb training
		param = {'nthread':4, 'max_depth':11, 'eta':0.03, 'subsample':0.75, 'colsample_bytree':0.85, 'eval_metric':'mlogloss', 'objective':'multi:softprob', 'num_class':5, 'verbose':1}
		num_round = 400
		dtrain = xgb.DMatrix(train_x, label=train_y)
		clf = xgb.train(param, dtrain, num_round) 		
		return clf
	   
	def _do_validation(self, clf, train_x, train_y, splited_key, logger):
		logger.info('splited_key[%s] do validation' % splited_key)
		# xgb training
		param = {'nthread':4, 'max_depth':11, 'eta':0.03, 'subsample':0.75, 'colsample_bytree':0.85, 'eval_metric':'mlogloss', 'objective':'multi:softprob', 'num_class':5, 'verbose':1}
		num_round = 400
		dtrain = xgb.DMatrix(train_x, label=train_y)
		res = xgb.cv(param, dtrain, num_round, nfold=3, metrics={ 'mlogloss' }, seed = 0)
		#res = xgb.cv(param, dtrain, num_round, nfold=3, metrics='mlogloss', seed = 0, verbose_eval=True, callbacks=[xgb.callback.print_evaluation(show_stdv=True)])
		logger.info('splited_key[%s] validation result' % (splited_key, str(res)))

	def _predict(self, clf, test_x, splited_key, logger):
		return clf.predict(xgb.DMatrix(test_x))

	def _output(self, predict_y, submission_filename, logger):
		np.savetxt(submission_filename, predict_y, delimiter=',')
