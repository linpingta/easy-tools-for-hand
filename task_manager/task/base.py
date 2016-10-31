#-*- coding: utf-8 -*-
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

"""
Define your own tasks with the following fieds:

Keyword arguments:
dimensions(required): list of attribute colum name
	for example: dimensions = [fb_account_id, country]
metrics(required): list of aggregate column num, default use sum(), could be replaced with {calc_method:metric_name}
	for example: metrics = [spend, {100*sum(clicks)/sum(impressions): ctr}]
filters(required): filter conditions, AND between each, no need to set dt here
	for example: filers = ['mobile_app_install > 0', 'video_id = ""']
orderby(required): list of attribute column name for order by with desc
	for example: orderby = [fb_account_id]
limit(required): number of rows returned, if no limit, set -1
"""


dimensions = ['fb_account_id', 'dt']
metrics = [{'sum(spend * relevance_score_score)/sum(spend)':'avg_relevance_score'}]
filters = [ 
	'mobile_app_install > 0',
	'video_id = ""',
	'fb_account_id = 12345'
]
orderby = []
limit = -1

