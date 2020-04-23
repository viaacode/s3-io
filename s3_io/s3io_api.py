#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 10:50:23 2020

@author: tina
"""

import json
import logging
import connexion
from flask import Flask, request
from s3_io.create_url_to_filesystem_task import process
from s3_io.task_info import remote_fetch_result
from s3_io.s3io_tools import SwarmS3Client
from s3_io.s3io_tasks import swarm_to_ftp, s3_to_ftp as s3_to_ftp_task
from viaa.observability import logging
from viaa.configuration import ConfigParser
config = ConfigParser()
logger = logging.get_logger('s3io', config)


logger = logging.get_logger('s3io', config)




def info(task_id):
    '''Gets state of a given task_id, parm state=true for task result'''
    default_error = json.dumps({'ERROR': 'No such id or wrong request'})
    try:
        logger.info('Fetching results from ES')


        state = request.args.get('state')
        if state == 'false':
            state = False
        else: state = True
        print(state)

        res = remote_fetch_result(task_id=task_id,
                                  state=state)

    except (ValueError, TypeError) as info_err:
        logger.error(info_err)
        res = json.dumps({'ERROR': str(info_err)})
    try:
        res = json.dumps(res)
        return res
    except (ValueError, TypeError):
        return str(res)
    return default_error

def s3_to_remote(**body):
    '''Async remote curl call'''
    logger.info(body)
    request_id = request.headers.get('x-request-id')
    body['remotefetch']['x-request-id'] = request_id
    task_ = process(body['remotefetch'])
    return str(task_)


def s3_to_ftp(async_task=True, **body):
    '''s3 naar ftp , async optional'''
    logger.info(body)
    request_id = request.headers.get('x-request-id')
    endpoint = body['s3toftp']['source']['domain']['name']
    obj = body['s3toftp']['source']['object']['key']
    key = config.app_cfg['S3_TO_FTP']['s3access_key']
    secret = config.app_cfg['S3_TO_FTP']['s3secret_key']
    bucket = body['s3toftp']['source']['bucket']['name']
    to_ftp = {
        'user': body['s3toftp']['destination']['user'],
        'password': body['s3toftp']['destination']['password'],
        'ftp_path': body['s3toftp']['destination']['path'],
        'ftp_host': body['s3toftp']['destination']['host']}
    if 'async' in request.args:
        if request.args['async'] is True:
            async_task = True


    if async_task:
        job = s3_to_ftp_task.s(body=body)
        dest_path = body['s3toftp']['destination']['path']
        task = job.apply_async(retry=True)
        job_id = task.id
        logger.info('task_id: %s for object_key %s to file %s',
                    job_id,
                    key,
                    dest_path,
                    correlationId=request_id)
        return str(job_id)

    SwarmS3Client(endpoint=endpoint,
                  obj=obj,
                  bucket=bucket,
                  secret=secret,
                  key=key,
                  to_ftp=to_ftp).to_ftp()
    return {'msg': 'ok'}, 201

def health():
    return {'msg': 'ok'}, 200

def create_app():

    app = connexion.App(__name__, port=8080, specification_dir='./api/')
    app.add_api('s3io-api.yaml', arguments={'title': 'Swarm s3'})
    return app

if __name__ == '__main__':
    create_app().run()
