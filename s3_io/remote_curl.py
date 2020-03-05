#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 13:11:15 2019
Remote curl space checker:

    Gdownload file with curl over ssh with paramiko

@author: tina
"""
import os
import threading
# from pymemcache.client import base
from functools import update_wrapper
import paramiko
import time
import requests
import json
from viaa.observability import logging
from viaa.configuration import ConfigParser
# from urllib3.util.retry import Retry
from json import JSONDecodeError

config = ConfigParser()
logger = logging.get_logger('s3io', config)


def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d


@decorator
def timeit(f):
    """time a function, used as decorator"""
    def result(*args, **kwargs):
        bt = time.time()
        r = f(*args, **kwargs)
        et = time.time()
        logger.debug("time spent on {0}: {1:.2f}s".format(f.__name__, et - bt))
        return r
    return result


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def buildRange(value, numsplits):
    lst = []
    part_size = value / numsplits
    for i in range(numsplits):
        if i == 0:
            lst.append('%s-%s' % (i, round(part_size)))
        else:
            lst.append('%s-%s' % (round(i * part_size) + 1,
                                  round(((i + 1) * part_size))))
        #logger.info(str(lst))
    logger.debug('Range parts:%s', str(lst))
    return lst


@timeit
def download_in_parts(url=None, dest_path=None, splitBy=4):
    """
    Download url in parts and join (locally)
    """
    if not url:
        logger.error("Please Enter some url to begin download.")
        raise OSError

    sizeInBytes = requests.head(
         url,
         allow_redirects=True,
         headers = {'host': 's3-qas.do.viaa.be',
                    'Accept-Encoding': 'identity'}).headers.get(
                    'content-length', None)
    logger.debug("%s bytes to download. from url: %s",
           str(sizeInBytes), url)
    if not sizeInBytes:
        logger.error("Size cannot be determined.")
    ranges = buildRange(int(sizeInBytes), splitBy)

    def downloadChunk(idx, irange):

        headers= {"host": "s3-qas.do.viaa.be",
                  "Range":'bytes={}'.format(irange)}
        logger.info(str(headers))
        req = requests.get(url,
                           headers=headers,
                           allow_redirects=True,
                           stream=True)
        with(open('filepart_'+ str(idx), 'ab')) as f:
            for chunk in req.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
    # create one downloading thread per chunk
    downloaders = [
        threading.Thread(
            target=downloadChunk,
            args=(idx, irange),

        )
        for idx, irange in enumerate(ranges)
        ]

    # start threads, let run in parallel, wait for all to finish
    for th in downloaders:
        th.start()
        logger.info('Thread started')
    for th in downloaders:
        th.join()
    if os.path.exists(os.path.split(dest_path)[0]):
        os.remove(dest_path)
    # reassemble file in correct order

    logger.info("Finished Writing %s fileparts ", str(splitBy))
    for i in range(0, len(ranges)):
        out_data = b''
        fn = 'filepart_' + str(i)
        with open(fn, 'rb') as fp:
            out_data += fp.read()
            with open(dest_path, 'ab') as fp:
                fp.write(out_data)


class RemoteCurl():
    """
    - run curl to download a file with paramiko ssh
    - Arguments:

         - url: the url to fetch

         - host: host the run curl on (ssh key user)

         - user: the ssh user

         - request_id: optional for logging

    """

    def __init__(self,
                 url,
                 dest_path,
                 host=None,
                 user=None,
                 headers=None,
                 parts=True,
                 request_id=None):
         # removed , after host
        self.host = host
        self.request_id = request_id
        self.fields = {"x-meemoo-request-id": self.request_id,
                       "RESULT": "STARTED"}
        if host is None:
            self.host = config.app_cfg['RemoteCurl']['host']
        self.user = user
        if user is None:
            self.user = config.app_cfg['RemoteCurl']['user']
        self.url = url
        self.dest_path = dest_path
        self.keyfile = config.app_cfg['RemoteCurl']['private_key_path']
        self.private_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        if headers:
            self.headers = headers
        if parts:
            self.tmp_dir, f = os.path.split(self.dest_path)
            b, _e = os.path.splitext(f)
            b = os.path.basename(os.path.normpath(b))
            self.tmp_dir = self.tmp_dir + '/work/' + b.rstrip()
            self.dest_path = os.path.join(self.tmp_dir, f)
        else:
            self.tmp_dir = os.path.split(dest_path)[0]

    @timeit
    def _remote_get(self):
        """Remote download from swarm to local filesystem curl + ssh"""
        fields = {}
        k = self.private_key#paramiko.RSAKey.from_private_key_file("/home/tina/.ssh/id_rsa")
        if k:
            remote_client = paramiko.SSHClient()
            remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_client.connect(self.host,
                                  port=22,
                                  username=self.user,)
            cmd = "mkdir -p {} &&".format(self.tmp_dir)+\
            "curl -w \"%{speed_download},%{http_code},%{size_download},%{url_effective},%{time_total}\n\" -L "+\
            " {} ".format(self.headers) +\
            " -s " + self.url +\
            " -o {} ".format(self.dest_path)+\
            " && echo SUCCESS || echo ERROR & exit 1"
            logger.info("Starting Remote CURL on %s: %s",
                        self.host,
                        str(cmd),
                        fields=self.fields)
            try:
                _stdin, stdout, stderr = remote_client.exec_command(cmd)
                out = stdout.readlines()
                if 'ERROR\n' in str(out[0]):
                    logger.error(str(stderr.readlines()),
                                 exc_info=True)
                result = str(out[1])
                speed = str(out[0]).split(',')
                fields = {'speed': speed[0],
                          'status_code': speed[1],
                          'filesize:': speed[2],
                          'source_url': speed[3],
                          'total_runtime': speed[4],
                          'x-meemoo-request-id': self.request_id,
                          'RESULT': 'FINISED'}
                logger.debug('setting stats in fields.. speed: %s Bytes/s,\
                             took: %s seconds',
                             speed[0],
                             speed[4],
                             fields=fields)
                if 'ERROR' in result:
                    fields['RESULT'] = 'FAILED'
                    fields['x-meemoo-request-id'] = self.request_id

                    logger.error('ERROR fetching: %s', str(speed[3]),
                                 exc_info=True,
                                 fields=fields)
                    raise OSError
                if 'SUCCESS' in result:
                    fields['RESULT'] = 'SUCCESS'
                    fields['x-meemoo-request-id'] = self.request_id

                    logger.info('result for fetching %s: %s ',
                                str(speed[3]),
                                str(result),
                                fields=fields)
                remote_client.close()
            except IOError as e:
                fields['RESULT'] = 'FAILED'
                fields['x-meemoo-request-id'] = self.request_id
                logger.error("failed to fetch url:%s, ERROR: %s",
                             self.url, str(e),
                             fields=fields)

            except ValueError as val_e:
                fields['RESULT'] = 'FAILED'

                logger.error(str(stdout.readlines()),
                             str(stderr.readlines()),
                             str(val_e),
                             fields=fields)
            return fields


    def __call__(self):
        '''Run remote_get'''
        return self._remote_get()


class RemoteAssembleParts():
    """Put the shit togetter"""

    def __init__(self,
                 tmp_dir=None,
                 dest_path=None,
                 host=None,
                 user=None,
                 request_id='x-meemoo-request-id'):
        self.dest_path = dest_path
        if tmp_dir is None:
            self.tmp_dir, f = os.path.split(self.dest_path)
        else:
            self.tmp_dir = tmp_dir
        b, _e = os.path.splitext(f)
        b = os.path.basename(os.path.normpath(b))
        self.tmp_dir = self.tmp_dir + '/work/' + b.rstrip()
        if host is None:
            self.host = config.app_cfg['RemoteCurl']['host']
        self.user = user,
        if user is None:
            self.user = config.app_cfg['RemoteCurl']['user']
        # self.url=url
        self.keyfile = config.app_cfg['RemoteCurl']['private_key_path']
        self.private_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        self.request_id = request_id
        self.fields = {}

    @timeit
    def _join_files(self):
        """
        Get the pct free of /export (the ftp datastore), using paramiko and df
        """
        k = self.private_key
        if k:
            remote_client = paramiko.SSHClient()
            remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_client.connect(self.host,
                                  port=22,
                                  username=self.user,)

            cmd = """cd {} &&
            if [ -f {} ]; then echo ERROR file exists; echo ERROR & exit 1; else
            for i in $(ls *part*);do cat $i  >> {};done;fi&&
            cd .. &&
            rm -rf {} &&
            echo SUCCESS ||echo ERROR""".format(self.tmp_dir,
                                                self.dest_path,
                                                self.dest_path,
                                                self.tmp_dir)
            logger.debug('Remote execute on %s:  %s',
                         self.host,
                         str(cmd.rstrip()))
            try:
                _stdin, stdout, stderr = remote_client.exec_command(cmd)
                out = stdout.readlines()
                err = stderr.readlines()
                if 'ERROR\n' in out:
                    self.fields['RESULT'] = 'FAILED'
                    self.fields['x-meemoo-request-id'] = self.request_id
                    logger.error(str(err)+str(out),
                                 exc_info=True,
                                 fields=self.fields)
                    raise IOError
                else:
                    self.fields['RESULT'] = 'SUCCESS'
                    self.fields['x-meemoo-request-id'] = self.request_id
                    logger.info('result for assemble %s: %s ',
                                str(self.dest_path),
                                str(out[0]).rstrip(),
                                fields=self.fields)
                remote_client.close()
            except IOError as e:
                logger.error("%s failed to fetch url:%s", str(e),
                             self.dest_path,
                             fields=self.fields)
                raise
            return self.fields

    def __call__(self):
        '''Join the files'''
        return self._join_files()



@timeit
def remote_fetch(url,
                 dest_path,
                 splitBy=8,
                 request_id=None):
    """Description:

         - download frorm url in parts and assemble to destpath

     Arguments:

          - host: remote hoistname
          - user: needs to have ssh key on remote host working!!

    """
    if not url:
        logger.error("Please Enter some url to begin download.")
        raise IOError
    fields={'RESULT': 'SCHEDULED',
            'x-meemoo-request-id': request_id}
    sizeInBytes = requests.head(url,
                                allow_redirects=True,
                                headers={'host': 's3-qas.viaa.be',
                                         'Accept-Encoding': 'identity'}).headers.get('content-length', None)
    logger.info("%s bytes to download. url: %s",
           str(sizeInBytes),str(url), fields=fields)
    if not sizeInBytes:
        logger.error( "Size cannot be determined url: %s.", url, fields=fields)
        raise requests.exceptions.HTTPError
    ranges = buildRange(int(sizeInBytes), splitBy)
    def downloadChunk(idx, irange):
        curl_headers = "-H 'host: s3-qas.viaa.be'"+\
                       " -H 'range: bytes={}' -r {}".format(irange, irange)
        RemoteCurl(url=url,
                   dest_path=dest_path + 'part' + str(idx),
                   request_id=request_id,
                   headers=curl_headers)()
    # create one downloading thread per chunk
    downloaders = [
        threading.Thread(
            target=downloadChunk,
            args=(idx, irange),

        )
        for idx, irange in enumerate(ranges)
        ]
    # Start the threads
    for th in downloaders:
        th.start()
        logger.debug('Thread started')
    # join the Threads!
    for th in downloaders:
        th.join()
    tmp_dir, _f = os.path.split(dest_path)
    b, _e = os.path.splitext(tmp_dir)
    tmp_dir = tmp_dir + '/temp' + b.rstrip()
    ## Assemble PARTS
    RemoteAssembleParts(tmp_dir=tmp_dir,
                        dest_path=dest_path)()
    fields = {'RESULT': 'SUCCESS',
              'x-meemoo-request-id': request_id}
    logger.info('Remote curl in parts and assemble for %s complete',
                dest_path,
                fields=fields)
    return dest_path


def remote_get(url,dest_path):
    """
    Downlod url to dest_path, using paramiko and curl
    """
    k = paramiko.RSAKey.from_private_key_file(
            config.app_cfg['RemoteCurl']['private_key_path'])
    if k:
        remote_client = paramiko.SSHClient()
        remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_client.connect(config.app_cfg['RemoteCurl']['host'],
                              port=22,
                              username=config.app_cfg['RemoteCurl']['user'],)

        cmd= "curl  -w \"%{speed_download},%{http_code},%{size_download},%{url_effective},%{time_total}\n\" -L " +\
        url + ' -o ' + dest_path+\
        " && echo SUCCESS || echo ERROR & exit 1"
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


def remote_ffprobe(mediafile, host=None, user=None):
    """Runs ffprobe on remote host"""
    if host == None:
        host = config.app_cfg['RemoteCurl']['host'],
        host = host[0]
    if user == None:
        user = config.app_cfg['RemoteCurl']['user']
    k = paramiko.RSAKey.from_private_key_file(
            config.app_cfg['RemoteCurl']['private_key_path'])
    if k:
        remote_client = paramiko.SSHClient()
        remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_client.connect(host,
                              port=22,
                              username=user,
                              )
        cmd= """ffprobe -show_format -show_streams -print_format json {} """.format(mediafile)
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
        except JSONDecodeError:
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

