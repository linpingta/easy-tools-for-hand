import os
import simplejson as json
import MySQLdb


class WeixinDbStorage(object):
    ''' Weixin db api
    '''
    @classmethod
    def init(cls, host='', user='', passwd='', port=3306):
	cls.host = host
	cls.user = user
	cls.passwd = passwd
	cls.port = port
	cls.conn = None
	cls.cur = None

    @classmethod
    def open_db_connect(cls, logger):
	pass

    @classmethod
    def close_db_connect(cls, logger):
	pass


class WeixinMySQLDbStorage(WeixinDbStorage):
    ''' Weixin Mysql DB API
    '''
    @classmethod
    def open_db_connect(cls, logger):
	try:
	    cls.conn = MySQLdb.connect(host=cls.host, user=cls.user, passwd=cls.passwd, port=cls.port, charset='utf8')
	    cls.cur = cls.conn.cursor()
	except Exception as e:
	    logger.exception(e)

    @classmethod
    def close_db_connect(cls, logger):
	try:
	    if cls.cur:
		cls.cur.close()
	    if cls.conn:
		cls.conn.close()
	except Exception as e:
	    logger.exception(e)

    @classmethod
    def get_users(cls, logger):
	db_users = []
	try:
	    # mock user here
	    db_user = {'nickname':'test', 'sex':1, 'open_id':'', 'language':'zh_CN', 'city': '', 'province':'', 'country': '', 'headimgurl':'', 'subscribe_time':12345, 'unionid':'', 'remark':'', 'groupid':0}
	    db_users.append(db_user)
	except Exception as e:
	    logger.exception(e)
	finally:
	    return db_users

    @classmethod
    def set_users(cls, wx_users, logger):
	try:
	    # inser user to db
	    pass
	except Exception as e:
	    logger.exception(e)
	
    
class WeixinTokenStorage(object):
    ''' Weixin token storage
    '''
    @classmethod
    def init(cls, logger=None):
	cls.app_to_token_dict = {}

    @classmethod
    def load(cls, logger=None):
	pass

    @classmethod
    def store(cls, logger=None):
	pass

    @classmethod
    def set_app_to_token_dict(cls, app_to_token_dict):
	cls.app_to_token_dict = app_to_token_dict

    @classmethod
    def get_app_to_token_dict(cls):
	return cls.app_to_token_dict


class WeixinTokenFileStorage(WeixinTokenStorage):
    ''' Weixin token stoarge in local file
    '''
    @classmethod
    def init(cls, storage_filename='', logger=None):
	cls.app_to_token_dict = {}
	cls.storage_filename = storage_filename
	cls.load(logger)

    @classmethod
    def load(cls, logger=None):
	if not cls.storage_filename:
	    logger.error('storage_place %s empty' % cls.storage_filename)
	else:
	    if os.path.exists(cls.storage_filename):
	        with open(cls.storage_filename, 'r') as fp_r:
		    cls.app_to_token_dict = json.load(fp_r)

    @classmethod
    def store(cls, logger=None):
	if not cls.storage_filename:
	    logger.error('storage_place %s empty' % cls.storage_filename)
	else:
	    with open(cls.storage_filename, 'w') as fp_w:
		json.dump(cls.app_to_token_dict, fp_w)
