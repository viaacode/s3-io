# Scalable Worker

> Auto-generated documentation for [s3_io.scalable_worker](../../s3_io/scalable_worker.py) module.

Created on Sat Jan 16 08:25:18 2021

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / Scalable Worker
    - [log_task_Started](#log_task_started)
    - [log_task_complete](#log_task_complete)
    - [on_celery_setup_logging](#on_celery_setup_logging)
    - [worker](#worker)

@author: tina

## log_task_Started

[[find in source code]](../../s3_io/scalable_worker.py#L33)

```python
@task_prerun.connect
def log_task_Started(sender, task_id, task, args, **kwargs):
```

RUNS ON TASK START

## log_task_complete

[[find in source code]](../../s3_io/scalable_worker.py#L24)

```python
@task_postrun.connect
def log_task_complete(sender, task_id, task, args, **kwargs):
```

Runs on task complete

## on_celery_setup_logging

[[find in source code]](../../s3_io/scalable_worker.py#L53)

```python
@setup_logging.connect
def on_celery_setup_logging(**kwargs):
```

tO MESS WITH THE LOGGER.

## worker

[[find in source code]](../../s3_io/scalable_worker.py#L62)

```python
def worker():
```

Starts the celery worker THREAD
