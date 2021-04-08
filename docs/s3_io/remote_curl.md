# RemoteCurl

> Auto-generated documentation for [s3_io.remote_curl](../../s3_io/remote_curl.py) module.

Created on Fri Aug  2 13:11:15 2019
Remote curl:

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / RemoteCurl
    - [RemoteCurl](#remotecurl)
        - [RemoteCurl().\_\_call\_\_](#remotecurl__call__)
        - [RemoteCurl().remote_get](#remotecurlremote_get)
    - [RemoteFetchException](#remotefetchexception)
    - [decorator](#decorator)
    - [remote_fetch](#remote_fetch)
    - [timeit](#timeit)

download file with curl over ssh with paramiko

#### Examples

```curl_headers="-H 'host:s3-domain.org"'"
r=RemoteCurl(url="http://10.50.152.194:80/tests3vents/0k2699098k-left.mp4", dest_path='/mnt/temptina/tmp/test 123456.x
```

- `@author` - tina

## RemoteCurl

[[find in source code]](../../s3_io/remote_curl.py#L179)

```python
class RemoteCurl():
    def __init__(
        url,
        dest_path,
        host=None,
        user=None,
        headers=None,
        request_id=None,
        password=None,
    ):
```

- run curl to download a file with paramiko ssh

- Arguments:

- url: the url to fetch

- host: host the run curl on (ssh key user)

- user: the ssh user

- password: user password

- request_id: optional for logging

### RemoteCurl().\_\_call\_\_

[[find in source code]](../../s3_io/remote_curl.py#L254)

```python
def __call__():
```

Run remote_get

### RemoteCurl().remote_get

[[find in source code]](../../s3_io/remote_curl.py#L229)

```python
@timeit
def remote_get():
```

Remote download from swarm to local filesystem curl + ssh

#### See also

- [timeit](#timeit)

## RemoteFetchException

[[find in source code]](../../s3_io/remote_curl.py#L31)

```python
class RemoteFetchException(Exception):
```

Exception raised when the remote fetch has failed

## decorator

[[find in source code]](../../s3_io/remote_curl.py#L37)

```python
def decorator(func_n):
```

Make function d a decorator: d wraps a function fn.

## remote_fetch

[[find in source code]](../../s3_io/remote_curl.py#L59)

```python
def remote_fetch(
    host,
    user,
    password,
    url,
    dest_path,
    tmp_dir=None,
    headers=None,
    request_id=None,
):
```

Remote download from swarm to local filesystem curl + ssh

## timeit

[[find in source code]](../../s3_io/remote_curl.py#L45)

```python
@decorator
def timeit(func_name):
```

time a function, used as decorator

#### See also

- [decorator](#decorator)
