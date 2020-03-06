# RemoteCurl

> Auto-generated documentation for [s3_io.remote_curl](../../s3_io/remote_curl.py) module.

Created on Fri Aug  2 13:11:15 2019
Remote curl space checker:

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / RemoteCurl
    - [RemoteAssembleParts](#remoteassembleparts)
        - [RemoteAssembleParts().\_\_call\_\_](#remoteassembleparts__call__)
    - [RemoteCurl](#remotecurl)
        - [RemoteCurl().\_\_call\_\_](#remotecurl__call__)
    - [buildRange](#buildrange)
    - [chunks](#chunks)
    - [decorator](#decorator)
    - [download_in_parts](#download_in_parts)
    - [remote_fetch](#remote_fetch)
    - [remote_ffprobe](#remote_ffprobe)
    - [remote_get](#remote_get)
    - [timeit](#timeit)

Gdownload file with curl over ssh with paramiko

#### Examples

```curl_headers="-H 'host:s3-domain.org"'"
r=RemoteCurl(url="http://10.50.152.194:80/tests3vents/0k2699098k-left.mp4?domain=s3-qas.viaa.be",
   dest_path='/mnt/temptina/tmp/test 123456.x```

@author: tina

## RemoteAssembleParts

[[find in source code]](../../s3_io/remote_curl.py#L275)

```python
class RemoteAssembleParts():
    def __init__(
        tmp_dir=None,
        dest_path=None,
        host=None,
        user=None,
        request_id='x-meemoo-request-id',
    ):
```

Put the shit togetter

### RemoteAssembleParts().\_\_call\_\_

[[find in source code]](../../s3_io/remote_curl.py#L360)

```python
def __call__():
```

Join the files

## RemoteCurl

[[find in source code]](../../s3_io/remote_curl.py#L145)

```python
class RemoteCurl():
    def __init__(
        url,
        dest_path,
        host=None,
        user=None,
        headers=None,
        parts=False,
        request_id=None,
    ):
```

- run curl to download a file with paramiko ssh

- Arguments:

- url: the url to fetch

- host: host the run curl on (ssh key user)

- user: the ssh user

- request_id: optional for logging

### RemoteCurl().\_\_call\_\_

[[find in source code]](../../s3_io/remote_curl.py#L270)

```python
def __call__():
```

Run remote_get

## buildRange

[[find in source code]](../../s3_io/remote_curl.py#L60)

```python
def buildRange(value, numsplits):
```

## chunks

[[find in source code]](../../s3_io/remote_curl.py#L54)

```python
def chunks(lst, n):
```

Yield successive n-sized chunks from lst.

## decorator

[[find in source code]](../../s3_io/remote_curl.py#L34)

```python
def decorator(d):
```

Make function d a decorator: d wraps a function fn.

## download_in_parts

[[find in source code]](../../s3_io/remote_curl.py#L74)

```python
@timeit
def download_in_parts(url=None, dest_path=None, splitBy=4):
```

#### Notes

- not used needs to run on host

Download url in parts and join (locally)

#### See also

- [timeit](#timeit)

## remote_fetch

[[find in source code]](../../s3_io/remote_curl.py#L366)

```python
@timeit
def remote_fetch(
    url,
    dest_path,
    splitBy=4,
    host=None,
    user=None,
    request_id=None,
):
```

Description:

- download frorm url in parts and assemble to destpath

#### Arguments

- `-` *host* - remote hoistname
- `-` *user* - needs to have ssh key on remote host working!!

#### See also

- [timeit](#timeit)

## remote_ffprobe

[[find in source code]](../../s3_io/remote_curl.py#L494)

```python
def remote_ffprobe(mediafile, host=None, user=None):
```

Runs ffprobe on remote host

## remote_get

[[find in source code]](../../s3_io/remote_curl.py#L433)

```python
def remote_get(url, dest_path):
```

Description:

- Downlod url to dest_path, using paramiko and curl

#### Arguments

- `-` *dest_path* - string

- url : string

## timeit

[[find in source code]](../../s3_io/remote_curl.py#L42)

```python
@decorator
def timeit(f):
```

time a function, used as decorator

#### See also

- [decorator](#decorator)
