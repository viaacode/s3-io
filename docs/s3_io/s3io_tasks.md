# S3io Tasks

> Auto-generated documentation for [s3_io.s3io_tasks](../../s3_io/s3io_tasks.py) module.

Created on Wed Jan  8 16:25:28 2020

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / S3io Tasks
    - [s3_to_ftp](#s3_to_ftp)
    - [swarm_to_ftp](#swarm_to_ftp)
    - [swarm_to_remote](#swarm_to_remote)

@author: tina

## s3_to_ftp

[[find in source code]](../../s3_io/s3io_tasks.py#L108)

```python
@app.task(max_retries=3, bind=True)
def s3_to_ftp(self, **body):
```

S3 to FTP

Description:

- Uses instance of class SwarmS3Client to_ftp call

- Streams from s3 to ftp

## swarm_to_ftp

[[find in source code]](../../s3_io/s3io_tasks.py#L33)

```python
@app.task(max_retries=5, bind=True)
def swarm_to_ftp(self, **body):
```

FTP to swarm function

## swarm_to_remote

[[find in source code]](../../s3_io/s3io_tasks.py#L62)

```python
@app.task(max_retries=5, bind=True)
def swarm_to_remote(self, **body):
```

URL to remote
