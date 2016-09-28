#-*- coding: utf-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import simplejson as json
from six.moves import http_client
import collections
import six

#app_id = 'wx415f5da962d67dac'
#app_secret = '152237c90eaccbc1d3f25247859b495d'

class WeixinSession(object):
    def __init__(self, app_id=None, app_secret=None, access_token=None):
	self.app_id = app_id
	self.app_secret = app_secret
	self.access_token = access_token

	self.session = requests.Session()
	params = {
	    'access_token': self.access_token
	}
	self.session.params.update(params)

    def update_params(self, params):
	self.session.params.update(params)


class WeixinResponse(object):

    """Encapsulates an http response from Weixin API."""

    def __init__(self, body=None, http_status=None, headers=None, call=None):
        """Initializes the object's internal data.

        Args:
            body (optional): The response body as text.
            http_status (optional): The http status code.
            headers (optional): The http headers.
            call (optional): The original call that was made.
        """
        self._body = body
        self._http_status = http_status
        self._headers = headers or {}
        self._call = call

    def jsonify_body(self):
	return json.loads(self._body)

    def body(self):
        """Returns the response body."""
        return self._body

    def json(self):
        """Returns the response body -- in json if possible."""
        try:
            return json.loads(self._body)
        except (TypeError, ValueError):
            return self._body

    def headers(self):
        """Return the response headers."""
        return self._headers

    def etag(self):
        """Returns the ETag header value if it exists."""
        return self._headers.get('ETag')

    def status(self):
        """Returns the http status code of the response."""
        return self._http_status

    def is_success(self):
        """Returns boolean indicating if the call was successful."""

        json_body = self.json()

        if bool(json_body):
            # Has body and no error
            if 'success' in json_body:
                return json_body['success']
            return True
        elif self._http_status == http_client.NOT_MODIFIED:
            # ETAG Hit
            return True
        elif self._http_status == http_client.OK:
            # HTTP Okay
            return True
        else:
            # Something else
            return False

    def is_failure(self):
        """Returns boolean indicating if the call failed."""
        return not self.is_success()

    def error(self):
        return FacebookRequestError(
            "Call was not successful",
            self._call,
            self.status(),
            self.headers(),
            self.body()
        )


class WeixinApi(object):

    _weixin_api = None

    def __init__(self, session):
	self._session = session
	self._num_requests_succeeded = 0
	self._num_requests_attempted = 0

    def get_num_requests_attempted(self):
        '''returns the number of calls attempted.'''
        return self._num_requests_attempted

    def get_num_requests_succeeded(self):
        '''returns the number of calls that succeeded.'''
	return self._num_requests_succeeded
	
    @classmethod
    def init(
        cls,
        app_id=None,
        app_secret=None,
        access_token=None,
    ):
        session = WeixinSession(app_id, app_secret, access_token)
        api = cls(session)
        cls.set_weixin_api(api)

    @classmethod
    def set_weixin_api(cls, api):
 	''' set WeixinApi instance'''
	cls._weixin_api = api

    @classmethod
    def get_weixin_api(cls):
 	''' get WeixinApi instance'''
	return cls._weixin_api

    def call(self, method, path, params=None, headers=None, files=None):
	''' make API call
	core function rely on requests.request
	'''
	if not params:
	    params = {}
	if not headers:
	    headers = {}
	if not files:
	    files = {}

	self._num_requests_attempted += 1

        if method in ('GET', 'DELETE'):
	    if params:
		self._session.update_params(params)

            response = self._session.session.request(
                method,
                path,
                headers=headers,
                files=files,
		verify=False,
            )
        else:
            if params:
                params = json.dumps(params, ensure_ascii=False).encode('utf-8')
            print 'params ', params

            response = self._session.session.request(
                method,
                path,
                data=params,
                headers=headers,
                files=files,
		verify=False,
            )
        weixin_response = WeixinResponse(
            body=response.text,
            headers=response.headers,
            http_status=response.status_code,
            call={
                'method': method,
                'path': path,
                'params': params,
                'headers': headers,
                'files': files,
            },
        )

        if weixin_response.is_failure():
            raise weixin_response.error()

        self._num_requests_succeeded += 1
        return weixin_response
