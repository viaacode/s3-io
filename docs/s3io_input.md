# S3io Input

> Auto-generated documentation for [s3io_input](../s3_io/s3io_input.py) module.

Created on Mon Jan 18 09:40:14 2021

- [S3io](README.md#s3io-index) / [Modules](MODULES.md#s3io-modules) / S3io Input
    - [log_task_Started](#log_task_started)
    - [log_task_complete](#log_task_complete)
    - [on_celery_setup_logging](#on_celery_setup_logging)
    - [quit_gracefully](#quit_gracefully)
    - [s3_api](#s3_api)

@author: tina

## log_task_Started

[[find in source code]](../s3_io/s3io_input.py#L33)

```python
@task_prerun.connect
def log_task_Started(sender, task_id, task, args, **kwargs):
```

RUNS ON TASK START

## log_task_complete

[[find in source code]](../s3_io/s3io_input.py#L24)

```python
@task_postrun.connect
def log_task_complete(sender, task_id, task, args, **kwargs):
```

Runs on task complete

## on_celery_setup_logging

[[find in source code]](../s3_io/s3io_input.py#L53)

```python
@setup_logging.connect
def on_celery_setup_logging(**kwargs):
```

tO MESS WITH THE LOGGER.

## quit_gracefully

[[find in source code]](../s3_io/s3io_input.py#L59)

```python
def quit_gracefully(t=None):
```

## s3_api

[[find in source code]](../s3_io/s3io_input.py#L76)

```python
def s3_api():
```
