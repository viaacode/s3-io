#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 13:38:51 2020

Discription:

    - Function to get the async result from the fxp celery result backend

    - Args:

        - task_id: Celery task uuid (the one you get after the service call)

        - state:

            - True for result status outcome

            - False for the result (in this case the original message)

Example:

    ```remote_fetch_result(task_id='6834be65-95af-41be-b1b8-68174f5068fe',
          state=False)```

@author: tina
"""
import logging
from os import path, remove
from celery import result
from celery.utils.log import get_logger
import json

LOGGER = get_logger('s3io')

def remote_fetch_result(task_id, state=False):
    '''

    - Grab the AsyncResult.

    - Returns state or result

    - Usage:

         - remote_fetch_result(task_id='e7fce5d9-ccbd-4d08-ae12-7888e6910215',
         state=True)
    '''
    try:
        if state:
            res = result.AsyncResult(task_id).state
            LOGGER.info("Task %s status %s ", task_id, res)
        else:
            LOGGER.info('RESULT request')
            res = result.AsyncResult(task_id).result
            LOGGER.info("Task %s result: %s ", task_id, str(res))
    except TypeError as type_err:
        LOGGER.error(type_err)
        res = False
    except ConnectionError as conn_e:
        LOGGER.error(conn_e)
        res = False
    if res:
        return res
