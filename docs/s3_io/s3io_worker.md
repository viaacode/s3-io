# S3io Worker

> Auto-generated documentation for [s3_io.s3io_worker](../../s3_io/s3io_worker.py) module.

Created on Mon Sep 23 11:58:05 2019

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / S3io Worker
    - [add_rabbithandler](#add_rabbithandler)
    - [log_task_Started](#log_task_started)
    - [log_task_complete](#log_task_complete)
    - [on_celery_setup_logging](#on_celery_setup_logging)
    - [quit_gracefully](#quit_gracefully)
    - [worker](#worker)

- Description:

- Start Celery worker from cli
- set concurrency here

- Kind:

- entrypoint

@author: tina

## add_rabbithandler

[[find in source code]](../../s3_io/s3io_worker.py#L39)

```python
def add_rabbithandler():
```

ADD a log handle to get task results in log

## log_task_Started

[[find in source code]](../../s3_io/s3io_worker.py#L55)

```python
@task_prerun.connect
def log_task_Started(sender, task_id, task, args, **kwargs):
```

RUNS ON TASK START

## log_task_complete

[[find in source code]](../../s3_io/s3io_worker.py#L46)

```python
@task_postrun.connect
def log_task_complete(sender, task_id, task, args, **kwargs):
```

Runs on task complete

## on_celery_setup_logging

[[find in source code]](../../s3_io/s3io_worker.py#L75)

```python
@setup_logging.connect
def on_celery_setup_logging(**kwargs):
```

tO MESS WITH THE LOGGER

## quit_gracefully

[[find in source code]](../../s3_io/s3io_worker.py#L81)

```python
def quit_gracefully(t=None):
```

## worker

[[find in source code]](../../s3_io/s3io_worker.py#L111)

```python
def worker():
```

sTARTS the celery worker THREAD
