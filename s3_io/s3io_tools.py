#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 10:50:45 2020

@author: tina
"""
import os
import boto3
import requests
import ftplib
import urllib
import io
from tqdm import tqdm
from functools import partial
from requests.adapters import HTTPAdapter
from botocore.exceptions import ClientError
import subprocess
import shlex
import shutil
import uuid
import json
from urllib3.util.retry import Retry
from urllib.parse import unquote
from viaa.observability import logging
from viaa.configuration import ConfigParser

config = ConfigParser()
swarmurl = config.app_cfg['castor']['swarmurl']
swarm_domain = config.app_cfg['castor']['swarmdomain']
logger = logging.get_logger('s3io', config)


class SwarmIo():
    """Description: streams file to ftp or local disk

    - Args:

        - bucket

        - key(object)

        - request_id (optional)

    - Kwargs on off these two:

        - to_ftp: dict:

                - user:
                    string
                - password:
                    string
                - ftp_path:
                    string
                - ftp_host:
                    string

        - to_file: dict:

                - path:
                    string

    """
    def __init__(self, bucket, key,
                 request_id=None,
                 progress=False,
                 to_ftp=None,
                 to_file=None,
                 **metadata):
        if  to_ftp is None:
            to_ftp={'user': None,
                    'password': None,
                    'ftp_path': None,
                    'ftp_host': None}
        if  to_file is None:
            to_file={'path': None}
        if request_id is None:
            self.request_id=str(uuid.uuid4())
        else:
            self.request_id=request_id

        self.key = key
        self.bucket = bucket
        key = unquote(self.key)
        self.log_fields={'x-viaa-request-id':self.request_id}
        logger.info("requesting object key info for: %s", self.key,
                    fields=self.log_fields)
        swarm_url = 'http://' + swarmurl
        self.headers={'host':swarm_domain}
        self.s = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=2,
                        status_forcelist=[502, 503, 504])
        self.url=swarm_url + '/' + self.bucket + '/' + self.key
        self.url.replace('//','/',1)
        self.s.mount('http://', HTTPAdapter(max_retries=retries))
        self.to_filesystem = to_file['path']
        self.to_ftp_user = to_ftp['user']
        self.to_ftp_password = to_ftp['password']
        self.to_ftp_path = to_ftp['ftp_path']
        self.ftp_host = to_ftp['ftp_host']



    def to_ftp(self, progress=False):

        """Description:

            - Create a url to stream to FTP

        Args:

            - progress:Boolean:

                    - Default False
                    - show tqdm progress bar if True
        """
        try:
            self.s.head(self.url)
        except ConnectionError as con_e:
            logger.error(str(con_e), exc_info=True, fields=self.log_fields)

        self.progress = progress
        ftp = ftplib.FTP(self.ftp_host)
        destpath = self.to_ftp_path
        ftp.login(self.to_ftp_user,
                  self.to_ftp_password)
        ftp.set_pasv(True)
        logger.info('streaming url: %s', self.url,
                    fields=self.log_fields)
        if self.progress:
            req = RequestIterator(self.url).as_progress()
        else:
            req = RequestIterator(self.url).as_stream()
        ftp.storbinary('STOR %s' % (destpath,), req)
        logger.info('FTP upload Finished for: %s',
                     destpath,
                     fields=self.log_fields)
    #    client.end_transaction('s3io_to_ftp_task', 200)
        return destpath

    def to_file(self):
        """Description:

            - GET url stream to stream to file

        """
        logger.info('Starting: to_file, for object: %s',
                    self.key)

        logger.info('##### Presignesd URL: %s #####',
                    self.url)
        try:
            o = DownloadFromSwarm(self.url, self.to_filesystem)()
            return str(o)
             #download_tofile(self.url,self.to_filesystem)()
        except Exception as gen_exc:
            logger.error(fields={'error':str(gen_exc),
                                 'x-meemoo-request-id':self.request_id})



#@elasticapm.capture_span()
class SwarmS3Client():
    """Description:

        - Streams s3 object to file or ftp path
        - endpoint/<bucket>/obj

    Args:

        - endpoint:
             s3 endpoint (like aws cli)

        - key:
            aws cli like access_key

        - secret:
            aws cli lile access_secret

        - obj:
            like aws cli KEY (the file, to stream)

        - bucket:
            aws like bucket

    Kwargs:

        - to_ftp: dict:

                - user:
                    string
                - password:
                    string
                - ftp_path:
                    string
                - ftp_host:
                    string

        - to_file: dict:

                - path:
                    string
    """
    def __init__(self, endpoint, obj, key, secret,
                 bucket,
                 progress=False,
                 to_ftp=None,
                 to_file=None,
                 **metadata):
        if  to_ftp is None:
            to_ftp={'user': None,
                    'password': None,
                    'ftp_path': None,
                    'ftp_host': None}
        if  to_file is None:
            to_file={'path': None}
        self.metadata = metadata
        self.progress = progress
        self.endpoint = endpoint
        self.key = key
        self.obj = obj
        self.secret = secret
        self.bucket = bucket
        self.to_filesystem = to_file['path']
        self.to_ftp_user = to_ftp['user']
        self.to_ftp_password = to_ftp['password']
        self.to_ftp_path = to_ftp['ftp_path']
        self.ftp_host = to_ftp['ftp_host']
        self.session = boto3.session.Session()
        logger.info(self.metadata)
        self.client= self.session.client(
                service_name='s3',
                aws_access_key_id = self.key,
                aws_secret_access_key = self.secret,
                endpoint_url=self.endpoint)

    def to_file(self):
        """Description:

            - Create a presigned url to stream to file
        """
        logger.info('Starting: to_file, for object: %s',
                    self.obj)
        url = self.signed_url()
        logger.info('##### Presignesd URL: %s #####',
                    url)
        stream_to_file(url, self.to_filesystem)
        return self.to_filesystem


    def to_ftp(self, progress=False):
        """Description:

            - Create a presigned url to stream to FTP

        Args:

            - progress:Boolean:

                    - Default False
                    - show tqdm progress bar if True
        """
        self.progress = progress
        url = self.signed_url()
        ftp = ftplib.FTP(self.ftp_host)
        destpath = self.to_ftp_path
        logger.info('Logging in with %s',
                    self.to_ftp_user)
        ftp.login(self.to_ftp_user,
                  self.to_ftp_password)
        ftp.set_pasv(True)
        logger.info('streaming url: %s', url)
        logger.debug(self.progress)
        if self.progress:
            print("######DISABLED#############")
        #    req =RequestIterator(url).as_progress()
        else:
            req = RequestIterator(url).as_stream()
        logger.info('FTP upload Starting ...')
        ftp.storbinary('STOR %s' % (destpath,), req)
        logger.info('FTP upload Finished for: %s ',
                    destpath)

        return destpath

    def signed_url(self):

        url = self.client.generate_presigned_url(
                'get_object', {'Bucket': self.bucket,
                               'Key': self.obj})
        return url

    def get_metadata(self):

        k = self.client.head_object(Bucket = self.bucket, Key = self.obj)
        if 'Metadata' in k:
            k = k["Metadata"]

        logger.info(k)

        return k
    def ffprobe_obj(self):
        cmd = "ffprobe -v quiet -print_format json -show_streams "
        args = shlex.split(cmd)
        args.append(self.signed_url())
        logger.info('running ' + str(args))
        ffprobeOutput = subprocess.check_output(args).decode('utf-8')
        ffprobeOutput = json.loads(ffprobeOutput)
        formatted=json.dumps(ffprobeOutput, sort_keys=False)
        return(str(formatted))


    def update_metadata_put(self):
        try:
            # retrieve the existing item to reload the contents
            response = self.client.get_object(Bucket=self.bucket, Key=self.obj)
            existing_body = response.get("Body").read()

            # set the new metadata
            new_metadata = self.metadata

            self.client.put_object(Bucket=self.bucket, Key=self.obj,
                                   Body=existing_body,
                                   Metadata=new_metadata)

            print("Metadata update (PUT) for {0} Complete!\n".format(self.obj))
        except ClientError as be:
            print("CLIENT ERROR: {0}\n".format(be))
        except Exception as e:
            logger.error("Unable to update metadata: {0}".format(e))

    def wipe_metadata_put(self):
        try:
            # retrieve the existing item to reload the contents
            response = self.client.get_object(Bucket=self.bucket, Key=self.obj)
            existing_body = response.get("Body").read()


            self.client.put_object(Bucket=self.bucket,
                                   Key=self.obj,
                                   Body=existing_body,
                                   Metadata={})

            print("Metadata update (PUT) for {0} Complete!\n".format(self.obj))
        except ClientError as be:
            logger.error("CLIENT ERROR: {0}\n".format(be))
        except Exception as e:
            logger.error("Unable to update metadata: {0}".format(e))

    def update_metadata(self):
        """Fails if key exists"""
        session = boto3.session.Session()
        s3_client = session.client(
                service_name='s3',
                aws_access_key_id = self.key,
                aws_secret_access_key = self.secret,
                endpoint_url=self.endpoint)
        k = s3_client.head_object(Bucket = self.bucket, Key = self.obj)
        m = k["Metadata"]

        for i in self.metadata:
            if check_key(m, i):
                logger.error('key %s exists',i )

        try:
            s3_client.copy_object(Bucket = self.bucket,
                               Key = self.obj,
                               CopySource = self.bucket + '/' + self.obj,
                               Metadata = self.metadata,
                               MetadataDirective='REPLACE')
        except ClientError as metadata_update_error:
            logger.error(metadata_update_error)

       # logger.info(m)

def check_key(dict, key):

    if key in dict.keys():
        logger.info("Key isPresent ! value: %s", dict[key])
        return True
    else:
        logger.info("Key isNotPresent ! value: %s", key)
        return False


#@elasticapm.capture_span()
class IteratorToStream(io.RawIOBase):
    """Description:

        - Access an iterator as a bytestream

    """
    def __init__(self, iterable, on_update=None):
        self._iterator = iterable
        self._on_update = on_update

    def read(self, size=None):
        try:
            res = next(self._iterator)
        except StopIteration:
            return
        if self._on_update:
            self._on_update()
        return res

#@elasticapm.capture_span()
class DownloadFromSwarm():
    """Description:

        - tqdm requests get , from swarm

    Args:

        - url:
            string

        - file:
            string

    Returns:

        - filesize:

            int
    """
    def __init__(self, url, file):
        self.url = url
        self.file = file

    def __call__(self):
        header = {"host":swarm_domain}
        file_size = int(
                requests.head(self.url,
                              headers=header,
                              allow_redirects=True).headers["Content-Length"])
        if os.path.exists(self.file):
            first_byte = os.path.getsize(self.file)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size
        header = {"Range": "bytes=%s-%s" % (first_byte, file_size),
                  "host":swarm_domain}
        pbar = tqdm(
            total=file_size, initial=first_byte,
            unit='B', unit_scale=True, desc=self.url.split('/')[-1])
        req = requests.get(self.url,
                           headers=header,
                           allow_redirects=True,
                           stream=True)
        with(open(self.file, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=49152):
                if chunk:
                    f.write(chunk)
                    pbar.update(49152)
        pbar.close()
        return file_size



#@elasticapm.capture_span()
class RequestIterator:
    """Description:

        - Iterates over `chunk_size` chunks of the contents of a file,
        - provides a tqdm progress indicator.
    """
    def __init__(self, url, chunk_size=20480, **kwargs):
        header = {"host":swarm_domain
        }
        req = urllib.request.Request(url, headers=header)
        self.file_size = int(urllib.request.urlopen(req).info(
                ).get('Content-Length', -1))
        self.first_byte = 0
        self.url = url
        header = {"host":swarm_domain,
                  "Range": "bytes=%s-%s" % (self.first_byte, self.file_size)
        }

        logger.debug('##### Copying %s #####',
                    str(header))

        self.req = requests.get(url,
                                headers=header,
                                stream=True,
                                **kwargs)
        self.chunk_size = chunk_size

    def __iter__(self):
        """Iters with chunck size"""
        return self.req.iter_content(self.chunk_size)

    def as_stream(self):
        """
        Returns a stream of the file contents.

        :return: IteratorToStream
        """
       #
        return IteratorToStream(iter(self))

    def as_progress(self):
        """Description:

            - Provides a tdqm progress meter

            - Returns a stream of the file contents.

        :return:

            - IteratorToStream
        """
        self.pbar = tqdm(total=self.file_size,
                     initial=self.first_byte,
                     unit='B',
                     unit_scale=True,
                     desc=self.url[-15:])
        return IteratorToStream(iter(self),
                                on_update=partial(self.pbar.update,
                                self.chunk_size))

#@elasticapm.capture_span()
def upload_file(endpoint, secret , key, file_name, bucket, object_name=None):
    """Description:

        - Upload a file to an S3 bucket


   :param file_name: File to upload
   :param bucket: Bucket to upload to
   :param object_name: S3 object name. If not specified file_name is used
   :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    session = boto3.session.Session()
    s3_client = session.client(
            service_name='s3',
            aws_access_key_id = key,
            aws_secret_access_key = secret,
            endpoint_url=endpoint)
    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logger.debug(str(response))
        logger.debug('File: %s, uploaded to %s/%s/%s',
                    file_name, endpoint,bucket,object_name)
    except ClientError as e:
        logger.error('ERROR: %s',str(e),exc_info=True)
        return False
    return True


#@elasticapm.capture_span()
def stream_to_file(url, dst):
    """Description:

        Downloads a file using the worker_helpers module

    Args:

        - url

            to download file

        - dst

            File path, place to put the file
    """
    logger.info('Starting downlod to : %s', dst)
    d = download_tofile(url, dst)()
    if os.path.isfile(dst):
        logger.debug('File %s downloaded', dst)
    else:
        raise FileNotFoundError
    return d


#@elasticapm.capture_span()
class download_tofile(object):
    def __init__(self, url, file):
        self.url = url
        self.file = file

    def __call__(self):

        r = requests.get(self.url, stream=True)
        if r.status_code == 200:
            logger.debug('starting downloading %s', self.file)
            with open(self.file, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        return self.file





if __name__ == "__main__":
    boto3.set_stream_logger(name='boto3', level=10, format_string=None)

