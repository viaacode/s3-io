# S3io Tasks

> Auto-generated documentation for [s3_io.s3io_tasks](../../s3_io/s3io_tasks.py) module.

Created on Wed Jan  8 16:25:28 2020

- [s3_io](../README.md#s3io) / [Modules](../MODULES.md#s3_io-modules) / [S3 Io](index.md#s3-io) / S3io Tasks
    - [s3_to_ftp](#s3_to_ftp)
    - [swarm_to_ftp](#swarm_to_ftp)
    - [swarm_to_remote](#swarm_to_remote)

@author: tina

## s3_to_ftp

[[find in source code]](../../s3_io/s3io_tasks.py#L97)

```python
@app.task(max_retries=3, bind=True)
def s3_to_ftp(self, **body):
```

S3 to FTP

## swarm_to_ftp

[[find in source code]](../../s3_io/s3io_tasks.py#L38)

```python
@app.task(max_retries=5, bind=True)
def swarm_to_ftp(self, **body):
```

FTP to swarm function

## swarm_to_remote

[[find in source code]](../../s3_io/s3io_tasks.py#L70)

```python
@app.task(max_retries=5, bind=True)
def swarm_to_remote(self, **body):
```

FTP to remote
