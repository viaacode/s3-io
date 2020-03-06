#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 14:12:09 2020
0k2699098k-left.mp4
@author: tina
"""

import uuid
from s3_io.s3io_tasks import swarm_to_remote
import configparser
from viaa.observability import logging
from viaa.configuration import ConfigParser
config = ConfigParser()
config_ = configparser.ConfigParser()
config_.read('/etc/viaa-workers/config.ini')
logger = logging.get_logger('s3io', config)
rnd = str(uuid.uuid4())
debug_msg = {"service_type": "celery",
             "service_name": "s3_to_filesystem",
             "service_version": "0.1",
             "x-meemoo-request-id": "thetefdSTReq___id",
             "source": {
                 "domain": {
                     "name": "s3-qas.viaa.be"
                      },
                 "bucket": {
                     "name": "tests3vents"
                      },
                 "object": {
                     "key": "0k2699098k-left.mp4"
                      }
                 },
             "destination": {
                 "path": "/mnt/temptina/" + rnd + ".MXF",
                 "host": "do-prd-tra-02.do.viaa.be",
                 "user": "tina"}}


def validate_input(msg):
    """
    Description:

         - Basic validation of a message
    """
    request_id = msg["x-meemoo-request-id"]
    key = msg['source']['object']['key']
    log_fields = {'x-meemoo-request-id': request_id}

    if 'path' in msg['destination']:
        logger.info('valid msg for object_key %s',
                    str(key),
                    fields=log_fields)
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
        request_id = msg["x-meemoo-request-id"]
        dest_path = msg["destination"]["path"]
        job = swarm_to_remote.s(body=msg)
        t = job.apply_async(retry=True)
        jobID = t.id
        log_fields = {'x-meemoo-request-id': request_id}
        logger.info('task Filesystem task_id: %s for object_key %s to file %s',
                    jobID,
                    key,
                    dest_path,
                    fields=log_fields)
        return t
    # else:
    logger.error('Not a valid message')
    return True

if __name__ == "__main__":
    process(debug_msg)
