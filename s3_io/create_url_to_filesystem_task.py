#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 14:12:09 2020

    - Validate incoming message and make a celry job to transfer a file from
    viaa swrm s3 to remote host

    - Uses celery signature:

        s3_io.s3io_tasks.swarm_to_remote.s(body=msg)

0k2699098k-left.mp4
@author: tina
"""

import uuid
from viaa.observability import logging
from viaa.configuration import ConfigParser
from s3_io.s3io_tasks import swarm_to_remote

config = ConfigParser()
logger = logging.get_logger('s3io.task_creator')
extra = {'app_name': 's3io'}

rnd = str(uuid.uuid4().hex)
debug_msg = {"service_type": "celery",
             "service_name": "s3_to_filesystem",
             "service_version": "0.1",
             "x-request-id": rnd,
             "source": {
                 "domain": {
                     "name": "s3-qas.viaa.be"},
                 "bucket": {
                     "name": "mam-highresvideo"},
                 "object": {
                     "key": "202007241019597010024191220005056B94C300000016432B00000D0F003957.mxf"}
                 },
             "destination": {
                 "path": "/home/tina/" + rnd + ".MXF",
                 "host": "dg-qas-tra-01.dg.viaa.be",
                 "user": "454",
                 "password":'12115@02106'}}


def validate_input(msg):
    """
    Description:

         - Basic validation of a message
    """

    request_id = msg["x-request-id"]
    key = msg['source']['object']['key']


    if 'path' in msg['destination']:
        logger.info('valid msg for object_key %s and request _id: %s',
                    str(key),
                    request_id,
                    correlationId=request_id,
                    extra=extra)
        return True
    return False


def _file(msg):
    return msg['s3']['object']['key']


def process(msg):
    """The processing:

          - starts a celery job

     Args:

          - msg: dict

     Returns:

          - task_id: string
     """
    if validate_input(msg):
        key = msg['source']['object']['key']
        request_id = msg["x-request-id"]
        dest_path = msg["destination"]["path"]
        job = swarm_to_remote.s(body=msg)
        celery_task = job.apply_async(retry=True)
        job_id = celery_task.id
        logger.info('task Filesystem task_id: %s for object_key %s to file %s',
                    job_id,
                    key,
                    dest_path,
                    cotrrelationId=request_id)
        return celery_task
    # else:
    logger.error('Not a valid message')
    return True

if __name__ == "__main__":
    process(debug_msg)
