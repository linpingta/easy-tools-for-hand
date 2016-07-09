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
			#tmp_breed = breed.replace(' Mix', '')
			#new_breed.extend(tmp_breed.split('/'))
			part_breeds = breed.split(' Mi')
			for part_breed in part_breeds:
				new_breed.extend(part_breed.split('/'))
		return new_breed

	def _transfer_color_input(self, origin_color, logger):
		new_color = []
		for color in origin_color:
			new_color.extend(color.split('/'))
		return new_color

	def _generate_combine_and_external_data(self, cleaned_train_data, cleaned_test_data, logger):

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

		return ((total_breed, total_color), ())

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

		#choices = ['Intact', 'Neutered', 'Spayed']
		choices = ['Intact']
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

	def _transfer_test_to_model(self, splited_key, splited_data, model_infos, combine_data, external_data, logger):
		if 'vectorizer_x' not in model_infos:
			logger.error('no vectorizer_x defined for model')
			return
		vectorizer_x = model_infos['vectorizer_x']
		(total_breed, total_color) = combine_data
		data = splited_data

		data['EncodeYear'] = data['DateTime'].apply(self._transfer_year_info)
		data['EncodeMonth'] = data['DateTime'].apply(self._transfer_month_info)
		data['EncodeWeekday'] = data['DateTime'].apply(self._transfer_weekday_info)
		data['EncodeHour'] = data['DateTime'].apply(self._transfer_hour_info)
		data['UnixDateTime'] = data['DateTime'].apply(self._transfer_unix_datetime_info)

		data['EncodeAgeuponOutcome'] = data['AgeuponOutcome'].apply(self._transfer_age_info)

		data = data[data['SexuponOutcome'] != '']

		data['NameLen'] = data['Name'].apply(self._transfer_name_len)
		for breed_type in total_breed:
			data[breed_type] = data['Breed'].apply(self._transfer_breed_type_info, args=(breed_type,))
		data['BreedMix'] = data['Breed'].apply(self._transfer_breed_mix_info)
		for color_type in total_color:
			data[color_type] = data['Color'].apply(self._transfer_color_type_info, args=(color_type,))
		data['ColorCount'] = data['Color'].apply(self._transfer_color_count_info)
		
		#data['Sex'] = data['SexuponOutcome'].apply(self._transfer_sex_info)
		#drop_list = ['Name', 'DateTime', 'AgeuponOutcome', 'SexuponOutcome', 'Breed', 'Color']
		drop_list = ['Name', 'DateTime', 'AgeuponOutcome', 'Breed', 'Color']

		transfer_data = data.drop(drop_list, 1)
		x = transfer_data.T.to_dict().values()
		encode_x = pd.DataFrame(vectorizer_x.transform(x))
		encode_matrix_x = xgb.DMatrix(encode_x)
		return encode_matrix_x
		#return encode_x

	def _transfer_data_to_model(self, splited_key, splited_data, combine_data, external_data, logger):
		(total_breed, total_color) = combine_data
		data = splited_data

		# encode y
		(encode_y, le_y) = self._encode_y(data['OutcomeType'].values, logger)

		data['EncodeYear'] = data['DateTime'].apply(self._transfer_year_info)
		data['EncodeMonth'] = data['DateTime'].apply(self._transfer_month_info)
		data['EncodeWeekday'] = data['DateTime'].apply(self._transfer_weekday_info)
		data['EncodeHour'] = data['DateTime'].apply(self._transfer_hour_info)
		data['UnixDateTime'] = data['DateTime'].apply(self._transfer_unix_datetime_info)

		data['EncodeAgeuponOutcome'] = data['AgeuponOutcome'].apply(self._transfer_age_info)

		data = data[data['SexuponOutcome'] != '']

		data['NameLen'] = data['Name'].apply(self._transfer_name_len)
		for breed_type in total_breed:
			data[breed_type] = data['Breed'].apply(self._transfer_breed_type_info, args=(breed_type,))
		data['BreedMix'] = data['Breed'].apply(self._transfer_breed_mix_info)
		
		for color_type in total_color:
			data[color_type] = data['Color'].apply(self._transfer_color_type_info, args=(color_type,))
		data['ColorCount'] = data['Color'].apply(self._transfer_color_count_info)
		#data['Sex'] = data['SexuponOutcome'].apply(self._transfer_sex_info)
		#drop_list = ['AnimalID', 'Name', 'DateTime', 'OutcomeType', 'OutcomeSubtype', 'AgeuponOutcome', 'SexuponOutcome', 'Breed', 'Color']
		drop_list = ['AnimalID', 'Name', 'DateTime', 'OutcomeType', 'OutcomeSubtype', 'AgeuponOutcome', 'Breed', 'Color']

		transfer_data = data.drop(drop_list, 1)
		print transfer_data.shape
		x = transfer_data.T.to_dict().values()
		vectorizer_x = DV(sparse=False)
		encode_x = pd.DataFrame(vectorizer_x.fit_transform(x))
		print encode_x.shape
		print encode_y.shape
		encode_x.to_csv('newdata')
		pd.DataFrame(encode_y).to_csv('newdata_y')

		#encode_x = transfer_data
		return (encode_x, encode_y, {'vectorizer_x':vectorizer_x, 'le_y':le_y})

	def _train(self, clf, train_x, train_y, splited_key, logger):
		logger.info('splited_key[%s] do training' % splited_key)
		# xgb training
		param = {'max_depth':11, 'eta':0.03, 'subsample':0.75, 'colsample_bytree':0.85, 'eval_metric':'mlogloss', 'objective':'multi:softprob', 'num_class':5, 'verbose':1}
		num_round = 4
		dtrain = xgb.DMatrix(train_x, label=train_y)
		clf = xgb.train(param, dtrain, num_round) 		
		return clf
		
	def _do_validation(self, clf, train_x, train_y, splited_key, logger):
		logger.info('splited_key[%s] do validation' % splited_key)
		# xgb training
		param = {'max_depth':11, 'eta':0.03, 'subsample':0.75, 'colsample_bytree':0.85, 'eval_metric':'mlogloss', 'objective':'multi:softprob', 'num_class':5, 'verbose':1}
		num_round = 4
		dtrain = xgb.DMatrix(train_x, label=train_y)
		xgb.cv(param, dtrain, num_round, nfold=3,
		       metrics='mlogloss', seed = 121, verbose_eval=True, callbacks=[xgb.callback.print_evaluation(show_stdv=True)])

	def _output_result(self, predict_y, submission_filename, logger):
            	np.savetxt(submission_filename, predict_y, delimiter=',')
