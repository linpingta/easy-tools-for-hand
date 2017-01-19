#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Email Sender"""
__author__ = 'linpingta@163.com'

from collections import OrderedDict

import smtplib
from smtplib import SMTPServerDisconnected
from email.mime.text import MIMEText

header = """<html><head>
<style>
th {
	background-color: #8EB31A;
	color: #fff;
	font-size: 14px;
	font-weight: bold;
	line-height: 20px;
	padding-top: 4px;
	border:1px solid #d2d6d9;
	text-align: center;
}

td { 
	border-top: 1px solid #d2d6d9;
	padding: 6px;
	font-size: 14px;
	color: #000;
	height: 20px;
	line-height: 20px;
	text-align: center;
	border-right:1px solid #8eb31a;
}

.odd td {
	background-color: #FFF;
}

.even td {
	background-color: #F0F9D6;
}

p {
	font-family: 'times new roman';
	font-weight: bold;
	font-size: x-large;
	font-variant: normal;
}
</style>
</head>
<body>
"""

footer = "</body></html>"

class EmailSender(object):
	""" 负责邮件发送的实例
	"""
	def __init__(self, conf, title):
		mailto_list = conf.get('email_sender', 'mailto_list')
		self.mailto_list = mailto_list.split(';')
		self.mail_host = conf.get('email_sender', 'mail_host')
		self.mail_user = conf.get('email_sender', 'mail_user')
		self.mail_passwd = conf.get('email_sender', 'mail_passwd')
		self._title = title
		self._head_content = ''
		self._content = ''

	def _send_content(self, title, content, logger):
		""" 发送邮件信息"""
		logger.debug('Sending Email To %s' % str(self.mailto_list))
		try:
			msg = MIMEText(content,_subtype='html',_charset='utf8')
			msg['From'] = self.mail_user
			msg['To'] = ";".join(self.mailto_list)
			msg['Subject'] = title

			s = smtplib.SMTP()  
			s.connect(self.mail_host)
			s.login(self.mail_user,self.mail_passwd)
			s.sendmail(self.mail_user, self.mailto_list, msg.as_string())
			s.quit()  
		except Exception, e:
			logger.exception(e)
			logger.debug('Email Sent Failed')
		else:
			logger.debug('Email Sent Success')

	def add_head_title(self, title, level=2):
		self._head_content += '<h%d>%s</h%d>' % (level, title, level)

	def add_head_table(self, table):
		self._head_content += table
		self._head_content += '<br/>'

	def add_title(self, title, level=2):
		self._content += '<h%d>%s</h%d>' % (level, title, level)

	def add_table(self, table):
		self._content += table											   
		self._content += '<br/>'											 
																			 
	def send(self, logger):										
		content = header + self._head_content + self._content + footer	   
		self._send_content(self._title, content, logger) 
