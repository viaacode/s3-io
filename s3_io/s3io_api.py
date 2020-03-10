#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 10:50:23 2020

@author: tina
"""

import json
import logging
import connexion
from flask import request, Flask
from s3_io.create_url_to_filesystem_task import process
from s3_io.task_info import remote_fetch_result
from s3_io.s3io_tools import SwarmS3Client

LOGGER = logging.getLogger('s3io')

def info(task_id):
    '''Gets state of a given task_id, parm state=true for task result'''
    default_error = json.dumps({'ERROR': 'No such id or wrong request'})
    try:
        LOGGER.info('Fetching results from ES')
        
        
        state = request.args.get('state')
        if state == 'false':
             state=False
        else: state = True  
        print(state)

        res = remote_fetch_result(task_id=task_id,
                                  state=state)
        
    except (ValueError, TypeError) as info_err:
        LOGGER.error(info_err)
        res = json.dumps({'ERROR': str(info_err)})
    try:
        res = json.dumps(res)
        return(res)
    except (ValueError, TypeError):
        return str(res)
    return default_error

def s3_to_remote(**body):
     LOGGER.info(body)
     request_id = request.headers.get('x-meemoo-request-id')
     body['remotefetch']['x-meemoo-request-id'] = request_id
     task_ = process(body['remotefetch'])
     return str(task_)

def s3_to_ftp(**body):
    LOGGER.info(body)
    request_id = request.headers.get('x-meemoo-request-id')
    SwarmS3Client().to_ftp()
 
  

if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, port=9090, specification_dir='./api/')
    app.add_api('s3io-api.yaml', arguments={'title': 'Swarm s3'})
    app.run()