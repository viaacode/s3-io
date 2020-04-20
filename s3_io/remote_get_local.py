#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 11:00:16 2020

@author: tina
"""

import json
import paramiko
from viaa.observability import logging#, correlation
from viaa.observability.correlation import CorrelationID
from viaa.configuration import ConfigParser
config = ConfigParser()
logger = logging.get_logger('s3io', config)


def remote_get(url, dest_path):
    """Description:

         - NOT USED atm

         - Downlod url to dest_path, using paramiko and curl

       Arguments:

            - dest_path: string

            - url : string

    """
    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_client.connect(config.app_cfg['RemoteCurl']['host'],
                          port=22,
                          username=config.app_cfg['RemoteCurl']['user'],
                          password=config.app_cfg['RemoteCurl']['passw'])

    cmd = "curl  -w \"%{speed_download},%{http_code},%{size_download},%{url_effective},%{time_total}\n\" -L " +\
    url + ' -o ' + dest_path + " && echo SUCCESS || echo ERROR & exit 1"
    try:
        _stdin, stdout, stderr = remote_client.exec_command(cmd)
        out = stdout.readlines()
        if stderr is not None:
            err = stderr.readlines()
            logger.error(str(err))
        result = str(out[1])
        speed = str(out[0]).split(',')
        fields = {'speed': speed[0],
                  'status_code': speed[1],
                  'filesize:': speed[2],
                  'source_url': speed[3],
                  'total_runtime': speed[4]}
        logger.debug('Recording SPEED  CURL.. speed: %s kiB/s, took: %s',
                     speed[0],
                     speed[4],
                     fields=fields)

        if 'ERROR' in result:
            fields['RESULT'] = 'FAILED'
            logger.error('ERROR fetching: %s',
                         str(speed[3]),
                         exc_info=True,
                         fields=fields)
            raise OSError
        fields['RESULT'] = 'SUCCESS'
        logger.info('result for fetching %s: %s ',
                    str(speed[3]),
                    str(result),
                    fields=fields)
        remote_client.close()

    except IOError as e:
        logger.error(str(e),
                     exc_info=True)
    return fields

