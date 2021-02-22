#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:25:28 2020

@author: tina
"""
import os
from viaa.observability import logging
from viaa.configuration import ConfigParser
from celery import Celery
import paramiko
from kombu import Exchange, Queue
from s3_io.s3io_tools import SwarmS3Client, SwarmIo
import s3_io.celeryconfig as celeryconfig
from s3_io.remote_curl import RemoteCurl, RemoteFetchException
from requests.exceptions import HTTPError
app = Celery('s3io',)
app.config_from_object(celeryconfig)
config = ConfigParser()
logger = logging.get_logger('s3io')
app.config_from_object(celeryconfig)
app.conf.task_queues = (Queue('s3io-prio',
                              Exchange('py-worker-s3io'),
                              routing_key='s3io-prio',
                              queue_arguments={'x-max-priority': 10}),
                        Queue('s3io-assemble', Exchange('py-worker-s3io'),
              routing_key='assamble-prio',
              queue_arguments={'x-max-priority': 5}))



app.conf.task_default_queue = 's3io-prio'
app.conf.task_default_exchange_type = 'direct'
#app.conf.task_default_routing_key = 's3io'

s3access_key = config.app_cfg['S3_TO_FTP']['s3access_key']
s3secret_key = config.app_cfg['S3_TO_FTP']['s3secret_key']
swarmurl = config.app_cfg['castor']['swarmurl']


@app.task(max_retries=5, bind=True)
def swarm_to_ftp(self, **body):
    '''FTP to swarm function'''
    dest_path = body['body']['dest_path']
    msg = body['body']
    # todo logic to get user/ pssw from body
    user = config.app_cfg['S3_TO_FTP']['ftpuser']
    passwd = config.app_cfg['S3_TO_FTP']['ftppassword']
    server = config.app_cfg['S3_TO_FTP']['ftpserver']
    logger.info('processing %s for object_key %s',
                dest_path,
                msg['s3']['object']['key'])
    try:

        SwarmIo(key=msg['s3']['object']['key'],
                bucket=msg['s3']['bucket']['name'],
                to_ftp={'user': user,
                        'password': passwd,
                        'ftp_path': dest_path,
                        'ftp_host': server}).to_ftp()
        logger.info('....Task id %s finished')
        return True
    except IOError as io_e:
        logger.error('#### ERROR %s : Task swarm_to_ftp failed',
                     str(io_e),
                     exc_info=True)
        raise self.retry(coutdown=1, exc=io_e, max_retries=2)


@app.task(max_retries=5, bind=True)
def swarm_to_remote(self, **body):
    """URL to remote"""

    logger.debug(str(body))
    dest_path = body['body']['destination']['path']
    body = body['body']
    #print(body['headers'])
    if 'user' in body['destination']:
        user = body['destination']['user']
        host = body['destination']['host']
        password = body['destination']['password']
    else:
        host = config.app_cfg['RemoteCurl']['host']
        user = config.app_cfg['RemoteCurl']['user']
        password = config.app_cfg['RemoteCurl']['passw']

    id_ = body['x-request-id']
    log_fields = {'x-request-id': id_}
    bucket = body['source']['bucket']['name']
    key = body['source']['object']['key']
    logger.info('process %s for object_key %s',
                dest_path,
                body['source']['object']['key'],
                extra=log_fields,
                correlationId=id_
                )
    try:
        url = 'http://' + swarmurl + '/' + bucket + '/' + key

        dest_file_path = RemoteCurl(url=url,
                                    dest_path=dest_path,
                                    host=host,
                                    user=user,
                                    headers=body['headers'],
                                    password=password,
                                    request_id=id_)()

        return str(dest_file_path)
    except RemoteFetchException as rf_e:
        logger.error('#### ERROR :Task swarm_to_remote failed for id %s. Retrying...',
                     str(self.request.id),
                     correlationId=id_,
                     exc_info=True)
        raise self.retry(coutdown=1, exc=rf_e, max_retries=5)






@app.task(max_retries=3, bind=True)
def assamble_parts(self, **body):

    body = body['kwargs']
  #  dest_path = body['body']['destination']['path']
    dest_path = body['destination']['path']
    dest_dir, _dest_file = os.path.split(dest_path)
    #body = body['body']
    id_ = body['x-request-id']

    if 'user' in body['destination']:
        user = body['destination']['user']
        host = body['destination']['host']
        password = body['destination']['password']
    else:
        host = config.app_cfg['RemoteCurl']['host']
        user = config.app_cfg['RemoteCurl']['user']
        password = config.app_cfg['RemoteCurl']['passw']

    cmd = """cd "{}" &&
    if [ -f "{}" ]; then echo ERROR file exists! & exit 1;fi
    SAVEIFS=$IFS
    IFS=$(echo -en "\\n\\b");
    if [ `ls {}.part?| wc -l` == 4 ];then echo all parts found;else echo ERROR not enough parts & exit 1;fi
    for i in $(ls {}.part?);
    do cat "$i" >> "{}.part" ;done &&
    mv "{}.part" "{}" && echo "SUCCESS";
    rm -rf {}.part* ||echo ERROR & exit 1; echo SUCCESS
    IFS=$SAVEIFS;

    """.format(
        dest_dir,
        dest_path,
        dest_path,
        dest_path,
        dest_path,
        dest_path,
        dest_path,
        dest_path,
        dest_path)
    with paramiko.SSHClient() as remote_client:
        try:
            remote_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_client.connect(host,
                                port=22,
                                username=user,
                                password=password)
            logger.info('Remote execute on %s:  %s',
                        host,
                        str(cmd.rstrip()),
                        correlationId=id_
                        )
            _stdin, stdout, stderr = remote_client.exec_command(cmd)
            out = stdout.readlines()
            err = stderr.readlines()
            self.extra = {}
            if out == [] or err != [] or 'ERROR' in out[0]:
                self.extra['RESULT'] = 'FAILED'
                self.extra['x-request-id'] = id_

                ssh_error = str(err)
                logger.error('stdout: ' + str(out) + ', bash ERROR:' + ssh_error,
                            exc_info=True,
                            extra=self.extra,
                            correlationId=id_
                            )
                raise IOError

            # else:

            self.extra['RESULT'] = 'DONE'

            self.extra['x-request-id'] = id_

            logger.info('result for assemble %s: %s ',
                        str(dest_path),
                        str(out[0]).rstrip(),
                        correlationId=id_,
                        extra=self.extra)
        except IOError as io_e:
            logger.error("%s failed to fetch url:%s", str(io_e),
                        dest_path,
                        extra=self.extra,
                        correlationId=id_,
                        exc_info=True)
            raise

    return dest_path
    #return body



@app.task(max_retries=3, bind=True)
def s3_to_ftp(self, **body):
    """S3 to FTP

    Description:

         - Uses instance of class SwarmS3Client to_ftp call

         - Streams from s3 to ftp

    """
    body = body['body']
    # the swager adds qury path to dict, so remove it
    if 's3toftp' in body:
        body = body['s3toftp']
    dest_path = body['destination']['path']
    logger.info('processing %s for object_key %s',
                dest_path,
                body['source']['object']['key'])
    user = body['destination']['user']
    password = body['destination']['password']
    dest_path = body['destination']['path']
    server = body['destination']['host']
    endpoint = body['source']['domain']['name']
    obj = body['source']['object']['key']
    bucket = body['source']['bucket']['name']
    try:
        SwarmS3Client(endpoint=endpoint,
                      key=s3access_key,
                      secret=s3secret_key,
                      obj=obj,
                      bucket=bucket,
                      to_ftp={'user': user,
                              'password': password,
                              'ftp_path': dest_path,
                              'ftp_host': server}).to_ftp()
        return True
    except IOError as io_e:
        raise self.retry(coutdown=1, exc=io_e, max_retries=2)

