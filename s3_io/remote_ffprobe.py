#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 10:52:53 2020

@author: tina
"""
import json
import paramiko
from viaa.observability import logging#, correlation
from viaa.observability.correlation import CorrelationID
from viaa.configuration import ConfigParser
from s3_io.create_url_to_filesystem_task import process
config = ConfigParser()
logger = logging.get_logger('s3io', config)

def remote_ffprobe(mediafile, host=None, user=None):
    """Runs ffprobe on remote host"""
    if host == None:
        host = config.app_cfg['RemoteCurl']['host'],
        host = host[0]
    if user == None:
        user = config.app_cfg['RemoteCurl']['user']

    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_client.connect(host,
                          port=22,
                          username=user,
                          password=config.app_cfg['RemoteCurl']['passw']
                          )
    cmd = """ffprobe -show_format -show_streams -print_format json {} """.format(mediafile)
    try:
        _stdin, stdout, stderr = remote_client.exec_command(cmd)

        out = stdout.readlines()
        o = list(map(lambda x: x.strip(), out))
        o = ''.join(out)
        p = json.loads(o)
        p['RESULT'] = 'SUCCESS'
        o = json.loads(str(o))
        remote_client.close()
        logger.info('ffprobed! %s ',
                    p["format"]["filename"],
                    fields=p)

        return o
    except json.JSONDecodeError:
        out = stderr.readlines()
        o = ''.join(out)
        p = {}
        p['RESULT'] = 'FAILED'
        logger.error('ffprobed FAILED! %s ',
                     str(o).strip(),
                     fields=p)
        remote_client.close()
        logger.error(str(out),
                     exc_info=True)
        raise IOError

    except KeyError:
        out = stderr.readlines()
        o = ''.join(out)
        p = {}
        p['RESULT'] = 'FAILED'
        logger.error('ffprobed FAILED! %s ',
                     str(o).strip(),
                     fields=p)
        remote_client.close()
        logger.error(str(out), exc_info=True)
        raise IOError
