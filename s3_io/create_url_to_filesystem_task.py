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
import json
import uuid
import requests
from viaa.observability import logging
from viaa.configuration import ConfigParser
from s3_io.s3io_tasks import swarm_to_remote, assamble_parts
from celery import chord
config = ConfigParser()
logger = logging.get_logger('s3io.task_creator')
extra = {'app_name': 's3-io'}

rnd = str(uuid.uuid4().hex)



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




def build_range(value, numsplits):
    """Returns list with ranges for parts download"""
    lst = []
    part_size = value / numsplits
    for i in range(numsplits):
        if i == 0:
            lst.append('%s-%s' % (i, round(part_size)))
        else:
            lst.append('%s-%s' % (round(i * part_size) + 1,
                                  round(((i + 1) * part_size))))
        # logger.info(str(lst))
    logger.debug('Range parts:%s', str(lst))
    return lst


def process(msg):
    """The processing:

         - starts a celery job

    Args:

         - msg: dict

    Returns:

         - task_id: string
    """
    downloaders = []
    assamble_msg = json.dumps(msg)
    if validate_input(msg):

        request_id = msg["x-request-id"]

        swarmurl = config.app_cfg['castor']['swarmurl']
        bucket = msg['source']['bucket']['name']
        key = msg['source']['object']['key']
        url = 'http://' + swarmurl + '/' + bucket + '/' + key
        host_header = config.app_cfg['RemoteCurl']['domain_header']
        size_in_bytes = requests.head(
            url,
            allow_redirects=True,
            headers={'host': host_header,
                     'Accept-Encoding': 'identity'}
            ).headers.get('content-length', None)
        logger.info("%s bytes to download. url: %s",
                    str(size_in_bytes), str(url),
                    correlationId=request_id,
                    extra=extra)
        if not size_in_bytes:
            logger.error("Size cannot be determined url: %s.",
                         url,
                         extra=extra,
                         correlationId=request_id
                         )
            raise requests.exceptions.HTTPError
        ranges = build_range(int(size_in_bytes), 4)
        dest_path = msg["destination"]["path"]

        for idx, irange in enumerate(ranges):
            prt_msg = msg

            dest_path_part = dest_path + '.part' + str(idx)
            prt_msg["destination"]["path"] = dest_path_part
            curl_headers = "-H 'host: {}'".format(host_header) + \
                           " -H 'range: bytes={}' -r {}".format(irange, irange)

            prt_msg['headers'] = curl_headers

            downloaders.append(json.dumps(prt_msg))


        prt_group =[]
        for d in downloaders:
            job = swarm_to_remote.si(body=json.loads(d)).set(
                                                      queue='s3io-prio')
            prt_group.append(job)

        jobs = chord(prt_group)(assamble_parts.si(args=None,
                                                  kwargs=json.loads(assamble_msg),
                                                  retry=True).set(
                                                      queue='s3io-assemble'))

    else:
        logger.error('Not a valid message')
        raise OSError
    return True

