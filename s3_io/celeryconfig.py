# -*- coding: utf-8 -*-
"""CONFIG for celery worker"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import configparser
from viaa.configuration import ConfigParser

CONFIG = ConfigParser()
#CONFIG.read('/etc/viaa-workers/config.ini')
worker_hijack_root_logger=False
if 'BROKER_URL' in os.environ:
    broker_url = os.environ.get('BROKER_URL')
else:
    broker_url = CONFIG.app_cfg['Celery']['broker_url']
BROKER_URL = CONFIG.app_cfg['Celery']['broker_url']
if 'RESULT_BACKEND' in os.environ:
    result_backend = os.environ.get('RESULT_BACKEND')
else:
    result_backend = CONFIG.app_cfg['Celery']['s3_result_backend']
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
result_persistent = True
