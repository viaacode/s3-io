#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:25:28 2020

@author: tina
"""
import configparser
from viaa.observability import logging
from viaa.configuration import ConfigParser
from celery import Celery
from kombu import Exchange, Queue
from s3_io.s3io_tools import SwarmS3Client, SwarmIo
import s3_io.celeryconfig as celeryconfig
from s3_io.remote_curl import remote_fetch

app = Celery('s3io',)
app.config_from_object(celeryconfig)
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
user = config.app_cfg['S3_TO_FTP']['ftpuser']
passwd = config.app_cfg['S3_TO_FTP']['ftppassword']
server = config.app_cfg['S3_TO_FTP']['ftpserver']
s3access_key = config.app_cfg['S3_TO_FTP']['s3access_key']
s3secret_key = config.app_cfg['S3_TO_FTP']['s3secret_key']


@app.task(max_retries=5, bind=True)
def swarm_to_ftp(self, **body):
    '''FTP to swarm function'''
    dest_path = body['body']['dest_path']
    msg = body['body']
    id_ = msg['responseElements']['x-viaa-request-id']
    log_fields = {'x-viaa-request-id': id_}

    logger.info('prcessing %s for object_key %s',
                dest_path,
                msg['s3']['object']['key'],
                fields=log_fields)
    try:

        SwarmIo(key=msg['s3']['object']['key'],
                bucket=msg['s3']['bucket']['name'],
                request_id=self.request.id,
                to_ftp={'user': user,
                        'password': passwd,
                        'ftp_path': dest_path,
                        'ftp_host': server}).to_ftp()
        logger.info('....Task id %s finished',
                    str(self.request.id))
        return True
    except IOError as io_e:
        logger.error('#### ERROR %s : Task swarm_to_ftp failed for id %s ',
                     str(io_e),
                     str(self.request.id),
                     exc_info=True)
        raise self.retry(coutdown=1, exc=io_e, max_retries=2)

@app.task(max_retries=5, bind=True)
def swarm_to_remote(self, **body):
    '''FTP to remote'''
    dest_path = body['body']['destination']['path']
    msg = body['body']
    id_ = msg['x-meemoo-request-id']
    log_fields = {'x-meemoo-request-id': id_}
    bucket = msg['source']['bucket']['name']
    key = msg['source']['object']['key']
    logger.info('process %s for object_key %s',
                dest_path,
                msg['source']['object']['key'],
                fields=log_fields)
    try:
        url = 'http://swarmget.do.viaa.be/' + bucket + '/' + key
        f = remote_fetch(url=url,
                         dest_path=dest_path,
                         host=config.app_cfg['RemoteCurl']['host'],
                         user=config.app_cfg['RemoteCurl']['user'],
                         request_id=id_)

        return str(f)
    except Exception as e:
        logger.error('#### ERROR %s :Task swarm_to_remote failed for id %s ',
                     str(e),
                     str(self.request.id),
                     exc_info=True)
        raise self.retry(coutdown=1, exc=e, max_retries=5)

@app.task(max_retries=3, bind=True)
def s3_to_ftp(self, **body):
    """S3 to FTP

    Description:

         - Uses instance of class SwarmS3Client to_ftp call t

         - Streams from s3 to ftp

    """
    logger.info(body)
    dest_path = body['body']['dest_path']
    logger.info('prcessing %s for object_key %s',
                dest_path,
                body['s3']['object']['key'])

    try:
        SwarmS3Client(endpoint='http://s3-qas.viaa.be/',
                      key=s3access_key,
                      secret=s3secret_key,
                      obj=body['s3']['object']['key'],
                      bucket=body['s3']['bucket']['name'],
                      to_ftp={'user': user,
                              'password': passwd,
                              'ftp_path': dest_path,
                              'ftp_host': server}).to_ftp()
        return True
    except IOError as io_e:
        raise self.retry(coutdown=1, exc=io_e, max_retries=2)
