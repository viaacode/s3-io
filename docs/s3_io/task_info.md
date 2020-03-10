# Task Info

> Auto-generated documentation for [s3_io.task_info](../../s3_io/task_info.py) module.

Created on Sat Mar  7 13:38:51 2020

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / Task Info
    - [remote_fetch_result](#remote_fetch_result)

Discription:

- Function to get the async result from the fxp celery result backend

- Args:

- task_id: Celery task uuid (the one you get after the service call)

- state:

- True for result status outcome

- False for the result (in this case the original message)

#### Examples

```remote_fetch_result(task_id='6834be65-95af-41be-b1b8-68174f5068fe',
state=False)```

@author: tina

## remote_fetch_result

[[find in source code]](../../s3_io/task_info.py#L35)

```python
def remote_fetch_result(task_id, state=False):
```

- Grab the AsyncResult.

- Returns state or result

- Usage:

- remote_fetch_result(task_id='e7fce5d9-ccbd-4d08-ae12-7888e6910215',
state=True)
