# RemoteCurl

> Auto-generated documentation for [s3_io.remote_curl](../../s3_io/remote_curl.py) module.

Created on Fri Aug  2 13:11:15 2019
Remote curl space checker:

- [s3_io](../README.md#s3_io-index) / [Modules](../MODULES.md#s3_io-modules) / [S3 Io](index.md#s3-io) / RemoteCurl
    - [KeepalivesFilter](#keepalivesfilter)
        - [KeepalivesFilter().filter](#keepalivesfilterfilter)
    - [MhRequest](#mhrequest)
    - [RemoteAssembleParts](#remoteassembleparts)
    - [RemoteCurl](#remotecurl)
    - [buildRange](#buildrange)
    - [chunks](#chunks)
    - [decorator](#decorator)
    - [download_in_parts](#download_in_parts)
    - [get_token](#get_token)
    - [remote_fetch](#remote_fetch)
    - [remote_ffprobe](#remote_ffprobe)
    - [remote_get](#remote_get)
    - [timeit](#timeit)

Gdownload file with curl over ssh with paramiko

@author: tina

## KeepalivesFilter

[[find in source code]](../../s3_io/remote_curl.py#L604)

```python
class KeepalivesFilter(object):
```

### KeepalivesFilter().filter

[[find in source code]](../../s3_io/remote_curl.py#L605)

```python
def filter(record):
```

## MhRequest

[[find in source code]](../../s3_io/remote_curl.py#L531)

```python
class MhRequest(object):
    def __init__(query, user, password, env='production', size=25, version=1):
```

## RemoteAssembleParts

[[find in source code]](../../s3_io/remote_curl.py#L255)

```python
class RemoteAssembleParts():
    def __init__(
        tmp_dir='/tmp',
        dest_path=None,
        host=None,
        user=None,
        request_id='x-meemoo-request-id',
    ):
```

Put the shit togetter

## RemoteCurl

[[find in source code]](../../s3_io/remote_curl.py#L142)

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

run curl to download a file with paramiko ssh

## buildRange

[[find in source code]](../../s3_io/remote_curl.py#L65)

```python
def buildRange(value, numsplits):
```

## chunks

[[find in source code]](../../s3_io/remote_curl.py#L59)

```python
def chunks(lst, n):
```

Yield successive n-sized chunks from lst.

## decorator

[[find in source code]](../../s3_io/remote_curl.py#L39)

```python
def decorator(d):
```

Make function d a decorator: d wraps a function fn.

## download_in_parts

[[find in source code]](../../s3_io/remote_curl.py#L78)

```python
@timeit
def download_in_parts(url=None, dest_path=None, splitBy=4):
```

Download url in parts and join (locally)

#### See also

- [timeit](#timeit)

## get_token

[[find in source code]](../../s3_io/remote_curl.py#L502)

```python
def get_token(self):
```

## remote_fetch

[[find in source code]](../../s3_io/remote_curl.py#L332)

```python
@timeit
def remote_fetch(
    url,
    dest_path,
    splitBy=8,
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

[[find in source code]](../../s3_io/remote_curl.py#L445)

```python
def remote_ffprobe(mediafile, host=None, user=None):
```

Get the pct free of /export (the ftp datastore), using paramiko and df

## remote_get

[[find in source code]](../../s3_io/remote_curl.py#L396)

```python
def remote_get(url, dest_path):
```

Downlod url to dest_path, using paramiko and curl

## timeit

[[find in source code]](../../s3_io/remote_curl.py#L47)

```python
@decorator
def timeit(f):
```

time a function, used as decorator

#### See also

- [decorator](#decorator)
