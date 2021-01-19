#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 08:25:18 2021

@author: tina
"""
import sys
import threading
import atexit
from s3_io.event_consumer import __main__ as Consume
from s3_io.s3io_api import __main__ as Api
from s3_io.s3io_tasks import app
from viaa.observability import logging
from viaa.configuration import ConfigParser
from celery.signals import setup_logging, task_postrun, task_prerun
from celery.result import AsyncResult


config = ConfigParser()
logger = logging.get_logger('s3io.scalable_worker', config)


@task_postrun.connect
def log_task_complete(sender, task_id, task, args, **kwargs):
    """Runs on task complete """
    # add_rabbithandler()
    result = AsyncResult(task_id).result
    if result is None:
        result = 'NO_RESULT_FOUND'


@task_prerun.connect
def log_task_Started(sender, task_id, task, args, **kwargs):
    """RUNS ON TASK START"""
    try:
        # add_rabbithandler()
        extra = {'celery_task_id': task_id,
                 'celery_task_name': str(task),
                 'x-viaa-request-id': task_id}
        logger.debug("prerun task: %s task_id: %s ",
                     str(task),
                     str(task_id),
                     extra=extra)
    except Exception as e:
        logger.error("error : %s/",
                     str(e),
                     exc_info=True,
                     extra=extra)


# to mess celery log you need this below
@setup_logging.connect
def on_celery_setup_logging(**kwargs):
    """tO MESS WITH THE LOGGER."""
    pass
    # return True




def worker():
    """Starts the celery worker THREAD"""
    argv = [
        "worker",
        "--loglevel=INFO",
        "-n=s3-io-worker@%h",
        "--concurrency=1",
        "-E",
    ]
    logger.info("********* starting the worker ********* ")
    app.worker_main(argv)

    print("FIN")


def __main__():
    worker()


if __name__ == '__main__':
    __main__()
