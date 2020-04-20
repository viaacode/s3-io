# Create Url To Filesystem Task

> Auto-generated documentation for [s3_io.create_url_to_filesystem_task](../../s3_io/create_url_to_filesystem_task.py) module.

Created on Tue Mar  3 14:12:09 2020

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / Create Url To Filesystem Task
    - [process](#process)
    - [validate_input](#validate_input)

- Validate incoming message and make a celry job to transfer a file from
viaa swrm s3 to remote host

- Uses celery signature:

s3_io.s3io_tasks.swarm_to_remote.s(body=msg)

0k2699098k-left.mp4
@author: tina

## process

[[find in source code]](../../s3_io/create_url_to_filesystem_task.py#L67)

```python
def process(msg):
```

The processing:

- starts a celery job

#### Arguments

- `-` *msg* - dict

#### Returns

- `-` *task_id* - string

## validate_input

[[find in source code]](../../s3_io/create_url_to_filesystem_task.py#L44)

```python
def validate_input(msg):
```

Description:

- Basic validation of a message
