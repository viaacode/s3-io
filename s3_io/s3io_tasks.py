#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:25:28 2020

@author: tina
"""
from viaa.observability import logging
from viaa.configuration import ConfigParser
from celery import Celery
from kombu import Exchange, Queue
import configparser
from s3_io.s3io_tools import SwarmS3Client, SwarmIo 
import s3_io.celeryconfig as celeryconfig
app = Celery('s3io',)
app.config_from_object(celeryconfig)
from s3_io.remote_curl import remote_fetch

config = ConfigParser()
logger = logging.get_logger('s3io', config)


app.config_from_object(celeryconfig)

app.conf.task_queues = (Queue('s3io',
                              Exchange('py-worker-s3io'),
                              routing_key='s3io'),)
app.conf.task_default_queue = 's3io'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 's3io'


config_ = configparser.ConfigParser()
config_.read('/etc/viaa-workers/config.ini')
#KEY = '000e1e7c4440.mxf'

user = config_['S3_TO_FTP']['ftpuser']
passwd =  config_['S3_TO_FTP']['ftppassword']
server =  config_['S3_TO_FTP']['ftpserver']
s3access_key = config_['S3_TO_FTP']['s3access_key']
s3secret_key = config_['S3_TO_FTP']['s3secret_key']



# from elasticapm import Client
# import elasticapm
# elasticapm.set_transaction_name('S3IO')
# elasticapm.set_transaction_result('SUCCESS')
# from elasticapm.contrib.celery import  register_instrumentation, register_exception_tracking
# client = Client({'SERVICE_NAME': 'S3IO',
#                  'DEBUG': False,
#                  'SERVER_URL': 
#                      'http://apm-server-prd.apps.do-prd-okp-m0.do.viaa.be:80'}) 
# register_instrumentation(client)
# register_exception_tracking(client)

# elasticapm.instrument()

@app.task(max_retries=5, bind=True)
def swarm_to_ftp(self, **body):
    '''FTP to swarm function'''
    dest_path = body['body']['dest_path']
    msg=body['body']
    id_ = msg['responseElements']['x-viaa-request-id']
    log_fields={'x-viaa-request-id': id_}

    logger.info('prcessing %s for object_key %s',
                dest_path,
                msg['s3']['object']['key'],
                fields=log_fields)
    try:
        
        SwarmIo(key=msg['s3']['object']['key'],
                bucket=msg['s3']['bucket']['name'],
                request_id=self.request.id,
                to_ftp={'user':user,
                        'password':passwd,
                        'ftp_path':dest_path,
                        'ftp_host':server}
                  ).to_ftp()  
        logger.info('....Task id %s finished', 
                      str(self.request.id))
        return True
    except Exception as e:
        logger.error('#### ERROR %s :Task swarm_to_ftp failed for id %s ', 
                     str(e),
                     str(self.request.id),
                     exc_info=True)
        raise self.retry(coutdown=1, exc=e, max_retries=5)

@app.task(max_retries=5, bind=True)
def swarm_to_remote(self, **body):
    '''FTP to remote'''
    dest_path = body['body']['destination']['path']
    msg=body['body']
    id_ = msg['x-meemoo-request-id']
    log_fields={'x-meemoo-request-id': id_}
    bucket=msg['source']['bucket']['name']
    key=msg['source']['object']['key']
    logger.info('process %s for object_key %s',
                dest_path,
                msg['source']['object']['key'],
                fields=log_fields)
    try:
        url='http://swarmget.do.viaa.be/'+ bucket + '/' + key
        f=remote_fetch(url=url, dest_path=dest_path, 
                       host='do-prd-tra-02.do.viaa.be', user='tina',
                       request_id=id_)
      
        return f
    except Exception as e:
        logger.error('#### ERROR %s :Task swarm_to_ftp failed for id %s ', 
                     str(e),
                     str(self.request.id),
                     exc_info=True)
        raise self.retry(coutdown=1, exc=e, max_retries=5)


@app.task(max_retries=3, bind=True)
def s3_to_ftp(self, **body):
    '''S3 to FTP'''
    logger.info(body)
    dest_path = body['body']['dest_path']
    #body=body['body']['Records'][0]
    logger.info('prcessing %s for object_key %s',
                dest_path,
                body['s3']['object']['key'])
        

    SwarmS3Client(endpoint='http://s3-qas.viaa.be/',
                  key=s3access_key,
                  secret=s3secret_key,
                  obj=body['s3']['object']['key'],
                  bucket=body['s3']['bucket']['name'],
                  to_ftp={'user':user,
                          'password':passwd,
                          'ftp_path':dest_path,
                          'ftp_host':server
                          }
                  ).to_ftp()  
    return True
