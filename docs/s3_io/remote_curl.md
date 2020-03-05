# RemoteCurl

> Auto-generated documentation for [s3_io.remote_curl](../../s3_io/remote_curl.py) module.

Created on Fri Aug  2 13:11:15 2019
Remote curl space checker:

- [s3_io](../README.md#s3io) / [Modules](../MODULES.md#s3_io-modules) / [S3 Io](index.md#s3-io) / RemoteCurl
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

@author: tina

## RemoteAssembleParts

[[find in source code]](../../s3_io/remote_curl.py#L262)

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

[[find in source code]](../../s3_io/remote_curl.py#L341)

```python
def __call__():
```

Join the files

## RemoteCurl

[[find in source code]](../../s3_io/remote_curl.py#L134)

```python
class RemoteCurl():
    def __init__(
        url,
        dest_path,
        host=None,
        user=None,
        headers=None,
        parts=True,
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

[[find in source code]](../../s3_io/remote_curl.py#L257)

```python
def __call__():
```

Run remote_get

## buildRange

[[find in source code]](../../s3_io/remote_curl.py#L56)

```python
def buildRange(value, numsplits):
```

## chunks

[[find in source code]](../../s3_io/remote_curl.py#L50)

```python
def chunks(lst, n):
```

Yield successive n-sized chunks from lst.

## decorator

[[find in source code]](../../s3_io/remote_curl.py#L30)

```python
def decorator(d):
```

Make function d a decorator: d wraps a function fn.

## download_in_parts

[[find in source code]](../../s3_io/remote_curl.py#L70)

```python
@timeit
def download_in_parts(url=None, dest_path=None, splitBy=4):
```

Download url in parts and join (locally)

#### See also

- [timeit](#timeit)

## remote_fetch

[[find in source code]](../../s3_io/remote_curl.py#L347)

```python
@timeit
def remote_fetch(url, dest_path, splitBy=8, request_id=None):
```

Description:

- download frorm url in parts and assemble to destpath

#### Arguments

- `-` *host* - remote hoistname
- `-` *user* - needs to have ssh key on remote host working!!

#### See also

- [timeit](#timeit)

## remote_ffprobe

[[find in source code]](../../s3_io/remote_curl.py#L468)

```python
def remote_ffprobe(mediafile, host=None, user=None):
```

Runs ffprobe on remote host

## remote_get

[[find in source code]](../../s3_io/remote_curl.py#L414)

```python
def remote_get(url, dest_path):
```

Downlod url to dest_path, using paramiko and curl

## timeit

[[find in source code]](../../s3_io/remote_curl.py#L38)

```python
@decorator
def timeit(f):
```

time a function, used as decorator

#### See also

- [decorator](#decorator)
