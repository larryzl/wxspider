#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/29 5:44 PM
@Author  : Larry
@Site    : 
@File    : mail_func.py
@Software: PyCharm
@Desc    :

"""

# !/usr/bin/env python3

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header


def sendMail(email, alert_info, file=None):
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	from email.mime.application import MIMEApplication

	username = "dev_service@tansuotv.com"
	password = "xx.=xx."
	sender = username
	receivers = ",".join([email])
	msg = MIMEMultipart()
	msg['Subject'] = 'VPN 开通提醒'
	msg['From'] = sender
	msg['To'] = receivers
	msg["Accept-Language"] = "zh-CN"
	msg["Accept-Charset"] = "ISO-8859-1,utf-8"

	puretext = MIMEText(alert_info, format, 'utf-8')
	msg.attach(puretext)

	try:
		client = smtplib.SMTP()
		client.connect('mail.tansuotv.com')
		client.login(username, password)
		client.sendmail(sender, receivers, msg.as_string())
		client.quit()
		print('mail send ok')
	except smtplib.SMTPRecipientsRefused:
		print('Recipient refused')
	except smtplib.SMTPAuthenticationError:
		print('Auth error')
	except smtplib.SMTPSenderRefused:
		print('Sender refused')
	except smtplib.SMTPException as e:
		print(e.message)


if __name__ == '__main__':
	import sys

	if len(sys.argv) != 3:
		print("参数错误\n./mail username password")
		sys.exit()
	username, password = sys.argv[1:]
	msg = "Dear, \n" \
	      "\n\t\tVPN账号已开通，\n" \
	      "\t\t用户名:\t%s\n" \
	      "\t\t密码:\t%s \n" \
	      "\t\tVPN服务器地址:\tvpn.tansuotv.cn\n" \
	      "\t\t秘钥:\ttansuo\n" \
	      "\t\t类型\tl2tp\n" \
	      "\n" \
	      "各系统添加VPN 介绍:\n" \
	      "MAC: http://www.etwiki.cn/mac-os/9402.html \n" \
	      "IOS: https://jingyan.baidu.com/article/456c463b2e7e7a0a5831442e.html \n" \
	      "Windows: https://jingyan.baidu.com/article/3a2f7c2e60af5c26afd61105.html\n" \
	      "安卓: http://service.tp-link.com.cn/detail_article_713.html" % (username, password)
	while 1:
		print("用户名:%s" % username)
		print("密码:%s" % password)
		confirm = input("确认发信信息(y/n):")
		if confirm == 'y':
			sendMail('%s@tansuotv.com' % username, msg)
		elif confirm == 'n':
			break
		else:
			continue
