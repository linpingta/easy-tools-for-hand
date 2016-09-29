#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :
#!/usr/bin/env python

import pandas as pd
import numpy as np
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter


if __name__ == '__main__':
	df = pd.read_csv('input_df.csv')
	df = df[df['avg_relevance_score'] > 0]
	d1 = df.groupby(['image_url'])['dt', 'avg_relevance_score']

	fig, ax = plt.subplots()
	legends = []
	for (image_url, image_data) in d1:
		print image_url
		image_url_info = '_'.join(image_url.split('_')[-2:])
		x = image_data['dt'].values
		y = image_data['avg_relevance_score'].values

		# treat x as datetime
		x_list = x.tolist()
		x_datetimes = []
		for x_value in x_list:
			x_datetime = datetime.datetime.strptime(str(x_value), '%Y%m%d')
			x_datetimes.append(x_datetime)

		# treat x as string
		#x_ticks = []
		#[ x_ticks.append(str(x_value)) for x_value in x_list ]
		#plt.xticks(x, x_ticks)

		plt.plot(x_datetimes, y)
		legends.append(image_url_info)

	plt.title(u'account_%d: image avg_relevance_score / dt' % 123456)
	ax.xaxis_date()
	ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
	fig.autofmt_xdate()
	legend = plt.legend(legends, loc='upper left', bbox_to_anchor=(1.05,1), borderaxespad=0.)

	plt.savefig('relevance_score.png', bbox_extra_artists=(legend,), bbox_inches='tight')

