# S3io Tools

> Auto-generated documentation for [s3_io.s3io_tools](../../s3_io/s3io_tools.py) module.

Created on Tue Jan  7 10:50:45 2020

- [s3_io](../README.md#s3io) / [Modules](../MODULES.md#s3_io-modules) / [S3 Io](index.md#s3-io) / S3io Tools
    - [DownloadFromSwarm](#downloadfromswarm)
    - [IteratorToStream](#iteratortostream)
        - [IteratorToStream().read](#iteratortostreamread)
    - [RequestIterator](#requestiterator)
        - [RequestIterator().\_\_iter\_\_](#requestiterator__iter__)
        - [RequestIterator().as_progress](#requestiteratoras_progress)
        - [RequestIterator().as_stream](#requestiteratoras_stream)
    - [SwarmIo](#swarmio)
        - [SwarmIo().to_file](#swarmioto_file)
        - [SwarmIo().to_ftp](#swarmioto_ftp)
    - [SwarmS3Client](#swarms3client)
        - [SwarmS3Client().ffprobe_obj](#swarms3clientffprobe_obj)
        - [SwarmS3Client().get_metadata](#swarms3clientget_metadata)
        - [SwarmS3Client().signed_url](#swarms3clientsigned_url)
        - [SwarmS3Client().to_file](#swarms3clientto_file)
        - [SwarmS3Client().to_ftp](#swarms3clientto_ftp)
        - [SwarmS3Client().update_metadata](#swarms3clientupdate_metadata)
        - [SwarmS3Client().update_metadata_put](#swarms3clientupdate_metadata_put)
        - [SwarmS3Client().wipe_metadata_put](#swarms3clientwipe_metadata_put)
    - [download_tofile](#download_tofile)
    - [check_key](#check_key)
    - [stream_to_file](#stream_to_file)
    - [upload_file](#upload_file)

@author: tina

## DownloadFromSwarm

[[find in source code]](../../s3_io/s3io_tools.py#L412)

```python
class DownloadFromSwarm():
    def __init__(url, file):
```

Description:
- tqdm requests get , from swarm

#### Arguments

- url:
    string
- file:
    string

#### Returns

- filesize:
    int

## IteratorToStream

[[find in source code]](../../s3_io/s3io_tools.py#L392)

```python
class IteratorToStream(io.RawIOBase):
    def __init__(iterable, on_update=None):
```

Description:

- Access an iterator as a bytestream

### IteratorToStream().read

[[find in source code]](../../s3_io/s3io_tools.py#L402)

```python
def read(size=None):
```

## RequestIterator

[[find in source code]](../../s3_io/s3io_tools.py#L462)

```python
class RequestIterator():
    def __init__(url, chunk_size=20480, **kwargs):
```

Description:

- Iterates over `chunk_size` chunks of the contents of a file,
- provides a tqdm progress indicator.

### RequestIterator().\_\_iter\_\_

[[find in source code]](../../s3_io/s3io_tools.py#L490)

```python
def __iter__():
```

Iters with chunck size

### RequestIterator().as_progress

[[find in source code]](../../s3_io/s3io_tools.py#L503)

```python
def as_progress():
```

Description:

- Provides a tdqm progress meter

- Returns a stream of the file contents.

#### Returns

- IteratorToStream

### RequestIterator().as_stream

[[find in source code]](../../s3_io/s3io_tools.py#L494)

```python
def as_stream():
```

Returns a stream of the file contents.

#### Returns

IteratorToStream

## SwarmIo

[[find in source code]](../../s3_io/s3io_tools.py#L37)

```python
class SwarmIo():
    def __init__(
        bucket,
        key,
        request_id=None,
        progress=False,
        to_ftp=None,
        to_file=None,
        **metadata,
    ):
```

Description: streams file to ftp or local disk

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

### SwarmIo().to_file

[[find in source code]](../../s3_io/s3io_tools.py#L146)

```python
def to_file():
```

Description:

- GET url stream to stream to file

### SwarmIo().to_ftp

[[find in source code]](../../s3_io/s3io_tools.py#L109)

```python
def to_ftp(progress=False):
```

Description:

- Create a url to stream to FTP

#### Arguments

- progress:Boolean:

- Default False
- show tqdm progress bar if True

## SwarmS3Client

[[find in source code]](../../s3_io/s3io_tools.py#L168)

```python
class SwarmS3Client():
    def __init__(
        endpoint,
        obj,
        key,
        secret,
        bucket,
        progress=False,
        to_ftp=None,
        to_file=None,
        **metadata,
    ):
```

Description:

- Streams s3 object to file or ftp path
- endpoint/<bucket>/obj

#### Arguments

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

- `-` *to_ftp* - dict:

- user:
    string
- password:
    string
- ftp_path:
    string
- ftp_host:
    string

- `-` *to_file* - dict:

- path:
    string

### SwarmS3Client().ffprobe_obj

[[find in source code]](../../s3_io/s3io_tools.py#L307)

```python
def ffprobe_obj():
```

### SwarmS3Client().get_metadata

[[find in source code]](../../s3_io/s3io_tools.py#L298)

```python
def get_metadata():
```

### SwarmS3Client().signed_url

[[find in source code]](../../s3_io/s3io_tools.py#L291)

```python
def signed_url():
```

### SwarmS3Client().to_file

[[find in source code]](../../s3_io/s3io_tools.py#L242)

```python
def to_file():
```

Description:

- Create a presigned url to stream to file

### SwarmS3Client().to_ftp

[[find in source code]](../../s3_io/s3io_tools.py#L256)

```python
def to_ftp(progress=False):
```

Description:

- Create a presigned url to stream to FTP

#### Arguments

- progress:Boolean:

- Default False
- show tqdm progress bar if True

### SwarmS3Client().update_metadata

[[find in source code]](../../s3_io/s3io_tools.py#L355)

```python
def update_metadata():
```

Fails if key exists

### SwarmS3Client().update_metadata_put

[[find in source code]](../../s3_io/s3io_tools.py#L318)

```python
def update_metadata_put():
```

### SwarmS3Client().wipe_metadata_put

[[find in source code]](../../s3_io/s3io_tools.py#L337)

```python
def wipe_metadata_put():
```

## download_tofile

[[find in source code]](../../s3_io/s3io_tools.py#L583)

```python
class download_tofile(object):
    def __init__(url, file):
```

## check_key

[[find in source code]](../../s3_io/s3io_tools.py#L381)

```python
def check_key(dict, key):
```

## stream_to_file

[[find in source code]](../../s3_io/s3io_tools.py#L558)

```python
def stream_to_file(url, dst):
```

Description:

Downloads a file using the worker_helpers module

#### Arguments

- url

to download file

- dst

File path, place to put the file

## upload_file

[[find in source code]](../../s3_io/s3io_tools.py#L524)

```python
def upload_file(endpoint, secret, key, file_name, bucket, object_name=None):
```

Description:

- Upload a file to an S3 bucket

#### Arguments

- `file_name` - File to upload
- `bucket` - Bucket to upload to
- `object_name` - S3 object name. If not specified file_name is used

#### Returns

True if file was uploaded, else False
