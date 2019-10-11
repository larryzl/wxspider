#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/23 10:42 AM
@Author  : Larry
@Site    : 
@File    : logger.py
@Software: PyCharm
@Desc    :

"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(BASE_LOG_DIR):
	os.mkdir(BASE_LOG_DIR)
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'standard': {
			'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
		},
		'error': {  # 错误日志输出格式
			'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(message)s'
		},
		'simple': {
			'format': '%(levelname)s %(asctime)s %(message)s'
		},
		'collect': {
			'format': '%(message)s'
		}
	},
	# 处理器：需要处理什么级别的日志及如何处理
	'handlers': {
		# 将日志打印到终端
		'console': {
			'level': 'DEBUG',  # 日志级别
			'class': 'logging.StreamHandler',  # 使用什么类去处理日志流
			'formatter': 'simple'  # 指定上面定义过的一种日志输出格式
		},
		# 默认日志处理器
		'default': {
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
			'filename': os.path.join(BASE_LOG_DIR, 'wxspider_debug.log'),  # 日志文件路径
			'maxBytes': 1024 * 1024 * 100,  # 日志大小 100M
			'backupCount': 5,  # 日志文件备份的数量
			'formatter': 'standard',  # 日志输出格式
			'encoding': 'utf-8',
		},
		# 日志处理级别warn
		'warn': {
			'level': 'WARN',
			'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
			'filename': os.path.join(BASE_LOG_DIR, "wxspider_warn.log"),  # 日志文件路径
			'maxBytes': 1024 * 1024 * 100,  # 日志大小 100M
			'backupCount': 5,  # 日志文件备份的数量
			'formatter': 'standard',  # 日志格式
			'encoding': 'utf-8',
		},
		# 日志级别error
		'error': {
			'level': 'ERROR',
			'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
			'filename': os.path.join(BASE_LOG_DIR, "wxspider_error.log"),  # 日志文件路径
			'maxBytes': 1024 * 1024 * 100,  # 日志大小 100M
			'backupCount': 5,
			'formatter': 'error',  # 日志格式
			'encoding': 'utf-8',
		},
	},
	'loggers': {
		# 默认的logger应用如下配置
		'': {
			'handlers': ['default', 'warn', 'error'],
			'level': 'DEBUG',
			'propagate': True,  # 如果有父级的logger示例，表示不要向上传递日志流
		},
		'django': {
			'handlers': ['console', 'default', 'warn', 'error'],
			'level': 'INFO',
		}
	},
}