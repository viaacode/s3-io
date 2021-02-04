# S3io Worker

> Auto-generated documentation for [s3io_worker](../s3_io/s3io_worker.py) module.

Created on Mon Sep 23 11:58:05 2019

- [S3io](README.md#s3io-index) / [Modules](MODULES.md#s3io-modules) / S3io Worker
    - [log_task_Started](#log_task_started)
    - [log_task_complete](#log_task_complete)
    - [on_celery_setup_logging](#on_celery_setup_logging)
    - [quit_gracefully](#quit_gracefully)
    - [s3_api](#s3_api)
    - [worker](#worker)

- Description:

- Start Celery worker from cli
- set concurrency here

- Kind:

- entrypoint

@author: tina

## log_task_Started

[[find in source code]](../s3_io/s3io_worker.py#L42)

```python
@task_prerun.connect
def log_task_Started(sender, task_id, task, args, **kwargs):
```

RUNS ON TASK START

## log_task_complete

[[find in source code]](../s3_io/s3io_worker.py#L33)

```python
@task_postrun.connect
def log_task_complete(sender, task_id, task, args, **kwargs):
```

Runs on task complete

## on_celery_setup_logging

[[find in source code]](../s3_io/s3io_worker.py#L62)

```python
@setup_logging.connect
def on_celery_setup_logging(**kwargs):
```

tO MESS WITH THE LOGGER.

## quit_gracefully

[[find in source code]](../s3_io/s3io_worker.py#L68)

```python
def quit_gracefully(t=None):
```

## s3_api

[[find in source code]](../s3_io/s3io_worker.py#L85)

```python
def s3_api():
```

## worker

[[find in source code]](../s3_io/s3io_worker.py#L111)

```python
def worker():
```

sTARTS the celery worker THREAD
