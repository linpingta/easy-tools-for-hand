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
</head>
<body>
"""
footer = "</body></html>"


class EmailSender(BaseSender):
	''' 负责邮件发送的实例
	'''
	def __init__(self, conf, title="EmailSender"):
		super(EmailSender, self).__init__(conf, title)

		self.mail_host = conf.get('email_sender', 'mail_host')
		self.mail_user = conf.get('email_sender', 'mail_user')
		self.mail_passwd = conf.get('email_sender', 'mail_passwd')

		self._content = ''
		self._mailto_list = []

	def _send_content(self, title, content, logger):
		""" 发送邮件信息"""
		logger.debug('Sending Email To %s' % str(self._mailto_list))
		back_message = ""
		try:
			if self._mailto_list:
				msg = MIMEText(content,_subtype='html',_charset='utf8')
				msg['From'] = self.mail_user
				msg['To'] = ";".join(self._mailto_list)
				msg['Subject'] = title

				s = smtplib.SMTP()
				s.connect(self.mail_host)
				s.login(self.mail_user,self.mail_passwd)
				s.sendmail(self.mail_user, self.mailto_list, msg.as_string())
				s.quit()
				logger.debug('Email Sent Success')
				back_message = "success"
			else:
				logger.debug('No mailto list defined')
				back_message = "no mailto_list"
			return back_message
		except Exception, e:
			logger.exception(e)

	@property
	def content(self):
		return self._content

	@content.setter
	def content(self, value):
		self._content = value

	def add_title(self, title, level=2):
		self._content += '<h%d>%s</h%d>' % (level, title, level)

	def add_table(self, table):
		self._content += table
		self._content += '<br/>'

	def send(self, logger):
		content = header + self._content + footer
		return self._send_content(self._title, content, logger)

	def set_sendto_list(self, sendto_users):
		self._mailto_list = sendto_users
