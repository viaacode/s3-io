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
import threading
from functools import update_wrapper
import paramiko
import requests
import logging
from viaa.configuration import ConfigParser
config = ConfigParser()
logger = logging.getLogger('s3io.remote_curl')
extra= {'app_name':'s3io'}


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


def chunks(lst, n_r):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n_r):
        yield lst[i:i + n_r]


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



def remote_fetch(host, user, password, url, dest_path, tmp_dir=None,
                 headers=None, request_id=None):
    """Remote download from swarm to local filesystem curl + ssh"""
    extra = {'host': host,
              'user': user,
              'dest_path': dest_path,
              'headers': headers}
    val_logger = logging.getLogger('s3io.remote_curl')

    val_logger = logging.LoggerAdapter(val_logger, extra)
    val_logger.debug('*****LOG extra*************: ' + str(extra))

    val_logger.info("Remote curl start from server %s",
                host,
                extra={'correlationId':request_id})
    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_client.connect(host,
                          port=22,
                          username=user,
                          password=password)
    cmd = "curl -w \"%{speed_download},%{http_code},%{size_download},%{url_effective},%{time_total}\" " + "-L -J {} ".format(headers) +\
        " -s " + url +\
        " -o \"{}\" || echo ERROR & exit 1".format(dest_path)
    if tmp_dir:
        logger.debug('create tmp_dir: %s', tmp_dir)
        cmd = """mkdir -p "{}"; """.format(tmp_dir) + cmd
    extra={'app_name':'s3io',
           'correlationId':request_id}
    val_logger = logging.getLogger('s3io.remote_curl')
    val_logger = logging.LoggerAdapter(val_logger, extra)

    val_logger.info("Starting Remote CURL on %s: %s",
                host,
                str(cmd),
                extra=extra)
    try:
        _stdin, stdout, stderr = remote_client.exec_command(cmd)
        out = stdout.readlines()
        err = stderr.readlines()
        logger.debug("stdout: " + str(out) + "stderr: "+ str(err))
        if stdout != []:
            result = 'SUCCESS'
            speed = str(out[0]).split(',')
            print(str(speed))
            extra = {'speed': speed[0],
                      'status_code': speed[1],
                      'filesize:': speed[2],
                      'source_url': speed[3],
                      'total_runtime': speed[4],
                      'x-request-id': request_id,
                      'RESULT': 'FINISED'}
            logging.LoggerAdapter(logger, extra)

            logger.info('setting stats in extra.. speed: %s Bytes/s,\
                        took: %s seconds',
                        speed[0],
                        speed[4],
                        extra=extra)

            extra['RESULT'] = 'SUCCESS'
            extra['x-request-id'] = request_id
            logging.LoggerAdapter(logger, extra)

            logger.info('SUCCESS for fetching %s: %s ',
                        str(speed[3]),
                        str(result),
                        extra=extra)
        else:
            extra['RESULT'] = 'FAILED'
            extra['x-request-id'] = request_id
            bash_error = str(stderr.readlines())

            err_logger = logging.LoggerAdapter(logger, extra)
            err_logger.error('ERROR fetching: %s, ERROR: %s', dest_path,
                             bash_error,
                             exc_info=True,
                             extra=extra)

        remote_client.close()
    except IOError as io_e:
        extra['RESULT'] = 'FAILED'
        extra['x-request-id'] = request_id
        logging.LoggerAdapter(logger, extra)
        logger.error("failed to fetch url:%s, ERROR: %s",
                     url, str(io_e),
                     extra=extra)

    except ValueError as val_e:
        extra['RESULT'] = 'FAILED'
        logging.LoggerAdapter(logger, extra)
        logger.error(str(stdout.readlines()),
                     str(stderr.readlines()),
                     str(val_e),
                     extra=extra)

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
                 parts=False,
                 request_id=None,
                 password=None):
        self.host = host,
        self.user = user
        self.password = password
        # see if we can use the chassis next line commented
        self.request_id = request_id
        # this not works in current context revert previous way
        # self.request_id = CorrelationID.correlation_id
        self.extra = {"RESULT": "STARTED"}
        self.host = host
        if host is None:
            self.host = config.app_cfg['RemoteCurl']['host']
        if user is None:
            self.user = config.app_cfg['RemoteCurl']['user']
        self.url = url
        self.dest_path = dest_path
        # create tmp_dir
        # dir_, file_name = os.path.split(self.dest_path)
        # base_name, _e = os.path.splitext(file_name)
        # base_name = os.path.basename(os.path.normpath(base_name))
        # self.tmp_dir = dir_ + "/." + base_name
        if password is None:
            self.password = config.app_cfg['RemoteCurl']['host']
        if headers:
            self.headers = headers
        else:
            self.headers = ''
        if parts:
            self.parts = True
            dir_, file_name = os.path.split(self.dest_path)
            base_name, _e = os.path.splitext(file_name)
            base_name = os.path.basename(os.path.normpath(base_name))
            self.tmp_dir_parts = dir_ + "/." + base_name
            self.dest_path_parts = os.path.join(self.tmp_dir_parts, file_name)
        else:
            self.parts = False

    @timeit
    def remote_get(self):
        """Remote download from swarm to local filesystem curl + ssh"""
        host_header = config.app_cfg['RemoteCurl']['domain_header']
        curl_headers = "-H 'host: {}'".format(host_header)
        self.headers = curl_headers

        extra = {'host': self.host,
                 'user': self.user,
                 'dest_path': self.dest_path,
                 'headers': self.headers}
        logging.LoggerAdapter(logger, extra)

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

    @timeit
    def download_chunk(self, idx, irange,
                       url,
                       dest_path,
                       user,
                       password,
                       request_id,
                       host):
        """
        Description:
            - RemoteCurl returns tmp_dir as string if parts is True,
              passes this to assamble (paramiko)

            - Start 4 download threads

            - Join the files (remote command paramiko)

        """
        host_header = config.app_cfg['RemoteCurl']['domain_header']

        curl_headers = "-H 'host: {}'".format(host_header) + \
                       " -H 'range: bytes={}' -r {}".format(irange, irange)
        self.headers = curl_headers
        self.dest_path_parts = dest_path + '_part_' + str(idx)
        remote_fetch(self.host,
                     self.user,
                     self.password,
                     self.url,
                     self.dest_path_parts,
                     self.tmp_dir_parts,
                     self.headers,
                     self.request_id)
        logger.info('Chunck %s downloaded to :%s', self.dest_path_parts,
                    self.tmp_dir_parts)

    @timeit
    def dwnl_parts(self):
        """Download parts"""
        host_header = config.app_cfg['RemoteCurl']['domain_header']
        extra = {'RESULT': 'SCHEDULED',
                 'x-request-id': self.request_id}

        logging.LoggerAdapter(logger, extra)

        size_in_bytes = requests.head(
            self.url,
            allow_redirects=True,
            headers={'host': host_header,
                     'Accept-Encoding': 'identity'}
            ).headers.get('content-length', None)
        logger.info("%s bytes to download. url: %s",
                    str(size_in_bytes), str(self.url),
                    extra=extra)
        if not size_in_bytes:
            logger.error("Size cannot be determined url: %s.",
                         self.url,
                         extra=extra)
            raise requests.exceptions.HTTPError
        ranges = build_range(int(size_in_bytes), 4)

        downloaders = [

            threading.Thread(
                target=self.download_chunk,
                args=(idx,
                      irange,
                      self.url,
                      self.dest_path_parts,
                      self.user,
                      self.password,
                      self.request_id,
                      self.host),

            )
            for idx, irange in enumerate(ranges)
            ]
        # Start the threads
        for dwnl_th in downloaders:
            dwnl_th.start()
            logger.debug('Thread started for %s',
                         self.dest_path)
        # join the Threads!
        for dwnl_th in downloaders:
            dwnl_th.join()
        # assamble parts
        remote_client = paramiko.SSHClient()
        remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_client.connect(self.host,
                              port=22,
                              username=self.user,
                              password=self.password)
        cmd = """cd "{}" &&
        if [ -f "{}" ]; then echo ERROR file exists! & exit 1;fi
        SAVEIFS=$IFS
        IFS=$(echo -en "\\n\\b");for i in $(ls *_part_?);do cat "$i" >> "{}.part" ;done && mv "{}.part" "{}" && echo "SUCCESS";IFS=$SAVEIFS
        cd ..
        rm -rf "{}" ||echo ERROR & exit 1; echo SUCCESS""".format(
            self.tmp_dir_parts,
            self.dest_path,
            self.dest_path,
            self.dest_path,
            self.dest_path,
            self.tmp_dir_parts)
        logger.info('Remote execute on %s:  %s',
                    self.host,
                    str(cmd.rstrip()))
        try:
            _stdin, stdout, stderr = remote_client.exec_command(cmd)
            out = stdout.readlines()
            err = stderr.readlines()
            if out == [] or err != [] or 'ERROR' in out[0]:
                self.extra['RESULT'] = 'FAILED'
                self.extra['x-request-id'] = self.request_id

                ssh_error = str(err)
                logger.error('stdout: ' + str(out) + ', bash ERROR:' + ssh_error,
                             exc_info=True,
                             extra=self.extra
                             )
                raise IOError

            # else:
            self.extra['RESULT'] = 'SUCCESS'
            self.extra['x-request-id'] = self.request_id

            logger.info('result for assemble %s: %s ',
                        str(self.dest_path),
                        str(out[0]).rstrip(),
                        extra=self.extra)
            remote_client.close()
        except IOError as io_e:
            logger.error("%s failed to fetch url:%s", str(io_e),
                         self.dest_path,
                         extra=self.extra,
                         exc_info=True)
            raise
        return self.dest_path

    def __call__(self):
        '''Run remote_get'''
        if not self.parts:
            return self.remote_get()
        parts_ = self.dwnl_parts()
        return str(parts_)



# url = 'http://swarmget.do.viaa.be/tests3vents/0k2699098k-left.mp4'
# test = RemoteCurl(url=url,
#                   dest_path='/mnt/temptina/test.test.1234 5.t658',
#                   request_id='test',
#                   parts=False)()
