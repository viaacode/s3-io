# S3io Api

> Auto-generated documentation for [s3_io.s3io_api](../../s3_io/s3io_api.py) module.

Created on Tue Jan  7 10:50:23 2020

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / S3io Api
    - [create_app](#create_app)
    - [health](#health)
    - [info](#info)
    - [s3_to_ftp](#s3_to_ftp)
    - [s3_to_remote](#s3_to_remote)

@author: tina

## create_app

[[find in source code]](../../s3_io/s3io_api.py#L104)

```python
def create_app():
```

## health

[[find in source code]](../../s3_io/s3io_api.py#L101)

```python
def health():
```

## info

[[find in source code]](../../s3_io/s3io_api.py#L27)

```python
def info(task_id):
```

Gets state of a given task_id, parm state=true for task result

## s3_to_ftp

[[find in source code]](../../s3_io/s3io_api.py#L62)

```python
def s3_to_ftp(async_task=True, **body):
```

s3 naar ftp , async optional

## s3_to_remote

[[find in source code]](../../s3_io/s3io_api.py#L53)

```python
def s3_to_remote(**body):
```

Async remote curl call
