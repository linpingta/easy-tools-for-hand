#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

""" Email Sender"""
__author__ = 'linpingta@163.com'

import smtplib
from smtplib import SMTPServerDisconnected
from email.mime.text import MIMEText

from base_sender import BaseSender

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
</style>
</head>
<body>
"""

footer = "</body></html>"

class EmailSender(object):
	''' 负责邮件发送的实例
	'''
	def __init__(self, conf, title):
		mailto_list = conf.get('email_sender', 'mailto_list')
		self.mailto_list = mailto_list.split(';')
		self.mail_host = conf.get('email_sender', 'mail_host')
		self.mail_user = conf.get('email_sender', 'mail_user')
		self.mail_passwd = conf.get('email_sender', 'mail_passwd')
		self.title = title

	def add_to_mailto_list(self, new_mailto_list, logger):
		self.mailto_list.extend(new_mailto_list)

	def _send_content(self, title, content, now, logger):
		''' 发送邮件信息'''
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

	def send(self, ad_headinfo, ad_objects, now, logger):
		try:
			content = ''

			head_name_s = ''
			for head_name in ad_headinfo:
				head_name_s += '<th>' + head_name + '</th>'
			head = '<tr>' + head_name_s + '</tr>'

			bodies = ''
			count = 1
			for ad_object in ad_objects:
				thebody = ''
				for ad_unit in ad_object:
					thebody = thebody + '<td>' + str(ad_unit) + '</td>'
				t =  'class="odd"' if count % 2 !=0 else 'class="even"'
				bodies = bodies + '<tr ' + t + ' >' + thebody + '</tr>'
				count += 1
				
			content = header + '<table border="1">' + head + bodies + '</table>' + footer
			self._send_content(self.title, content, now, logger)
		except Exception as e:
			logger.exception(e)
