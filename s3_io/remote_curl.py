#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 13:11:15 2019
Remote curl:

    download file with curl over ssh with paramiko

Examples:

```curl_headers="-H 'host:s3-domain.org"'"
r=RemoteCurl(url="http://10.50.152.194:80/tests3vents/0k2699098k-left.mp4", dest_path='/mnt/temptina/tmp/test 123456.x
```

@author: tina
"""
import os
import time
from functools import update_wrapper
import paramiko
from paramiko.ssh_exception import SSHException
from viaa.observability import logging
from viaa.configuration import ConfigParser
config = ConfigParser()
logger = logging.get_logger('s3io.remote_curl')


class RemoteFetchException(Exception):
    """ Exception raised when the remote fetch has failed
    """
    pass


def decorator(func_n):
    "Make function d a decorator: d wraps a function fn."
    def _d(f_n):
        return update_wrapper(func_n(f_n), f_n)
    update_wrapper(_d, func_n)
    return _d


@decorator
def timeit(func_name):
    """time a function, used as decorator"""
    def result(*args, **kwargs):
        b_t = time.time()
        rtn_f = func_name(*args, **kwargs)
        e_t = time.time()
        logger.debug("time spent on {0}: {1:.2f}s".format(func_name.__name__,
                                                          e_t - b_t))
        return rtn_f
    return result



def remote_fetch(host, user, password, url, dest_path, tmp_dir=None,
                 headers=None, request_id=None):
    """Remote download from swarm to local filesystem curl + ssh"""
    extra = {'host': host,
             'user': user,
             'dest_path': dest_path,
             'headers': headers}

    curl_cmd = "curl -w \"%{speed_download},%{http_code},%{size_download},%{url_effective},%{time_total}\" " + "-L -J {} ".format(headers) +\
        " -S -s " + url +\
        " -o \"{}\" || rm {} ;echo ERROR; exit 1".format(dest_path, dest_path)
    check_cmd = """ if [ -f "{}" ] ;then echo ERROR & exit 1;fi && """.format(
        dest_path)
    cmd = check_cmd + curl_cmd

    with paramiko.SSHClient() as remote_client:
        try:
            remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_client.connect(host,
                                  port=22,
                                  username=user,
                                  password=password)
            extra = {'app_name': 's3-io',
                     'correlationId': request_id}
            logger.info("Starting Remote CURL on %s: %s",
                        host,
                        str(cmd),
                        extra=extra,
                        correlationId=request_id)
            _stdin, stdout, stderr = remote_client.exec_command(cmd)
            out = stdout.readlines()
            err = stderr.readlines()
            speeds = []
            logger.debug("stdout: " + str(out) + "stderr: " + str(err))

            if err:
                # retry
                extra['RESULT'] = 'FAILED'
                extra['x-request-id'] = request_id
                bash_error = str(err)

                logger.error('ERROR fetching: %s, ERROR: %s', dest_path,
                             bash_error,
                             exc_info=True,
                             correlationId=request_id,
                             extra=extra)
                raise RemoteFetchException
            if out:
                try:
                    speed = out[0].split(',')
                    speeds.append(speed[0])
                    status_code = speed[1]
                    if int(status_code) >= 400:
                        extra = {'speed': speed[0],
                                 'status_code': speed[1],
                                 'filesize:': speed[2],
                                 'source_url': speed[3],
                                 'total_runtime': speed[4],
                                 'x-request-id': request_id,
                                 'RESULT': 'FAILED'}
                        logger.error(
                            'ERROR remote fetch failed with status code: %s',
                            speed[1],
                            extra=extra,
                            correlationId=request_id
                            )
                        raise RemoteFetchException
                    extra = {'speed': speed[0],
                             'status_code': speed[1],
                             'filesize:': speed[2],
                             'source_url': speed[3],
                             'total_runtime': speed[4],
                             'x-request-id': request_id,
                             'RESULT': 'FINISHED'}
                    logger.info('Task DONE, speed: %s Bytes/s,\
                                took: %s seconds',
                                speed[0],
                                speed[4],
                                extra=extra,
                                correlationId=request_id
                                )

                except IndexError:
                    logger.error(
                        "ERROR fetch failed: " + str(dest_path),
                        correlationId=request_id
                    )
                    raise RemoteFetchException

        except SSHException as ssh_e:
            extra['RESULT'] = 'FAILED'
            logger.error(str(ssh_e),
                         correlationId=request_id,
                         extra=extra)
            raise RemoteFetchException

    return dest_path




class RemoteCurl():
    """
    - run curl to download a file with paramiko ssh

    - Arguments:

         - url: the url to fetch

         - host: host the run curl on (ssh key user)

         - user: the ssh user

         - password: user password

         - request_id: optional for logging

    """

    def __init__(self,
                 url,
                 dest_path,
                 host=None,
                 user=None,
                 headers=None,
                 request_id=None,
                 password=None):
        self.host = host,
        self.user = user
        self.password = password
        self.request_id = request_id
        self.extra = {"RESULT": "STARTED"}
        self.host = host
        if host is None:
            self.host = config.app_cfg['RemoteCurl']['host']
        if user is None:
            self.user = config.app_cfg['RemoteCurl']['user']
        self.url = url
        self.dest_path = dest_path
        if password is None:
            self.password = config.app_cfg['RemoteCurl']['host']
        if headers:
            self.headers = headers
        else:
            self.headers = ''


    @timeit
    def remote_get(self):
        """Remote download from swarm to local filesystem curl + ssh"""
        # host_header = config.app_cfg['RemoteCurl']['domain_header']
        # curl_headers = "-H 'host: {}'".format(host_header)
        # self.headers = curl_headers

        extra = {'host': self.host,
                 'user': self.user,
                 'dest_path': self.dest_path,
                 'headers': self.headers}

        logger.info("Remote curl start from server %s",
                    self.host,
                    extra=extra)
        remote_fetch(self.host,
                     self.user,
                     self.password,
                     self.url,
                     self.dest_path,
                     None,
                     self.headers,
                     self.request_id)
        return(self.dest_path)

    def __call__(self):
        """Run remote_get"""
        self.remote_get()
