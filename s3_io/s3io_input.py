#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:40:14 2021

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
logger = logging.get_logger('s3io.input', config)


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

def quit_gracefully(t=None):
    logger.warning("######### sending app.control.shutdown() DISABLED########")
    # a=app.control.shutdown()
    a = 'ERROR'
    # worker_process_shutdown
    logger.warning('######### Bye, this is it i am Quiting ######### %s', a)
    if t is not None:
        try:
            logger.warning("KILLING thread!")
            t.join()
          #  sys.exit(0)
        except Exception as e:
            logger.error(str(e),
                         exc_info=True)

    exit(0)

def s3_api():
    try:
        logger.info('*********** Starting API ************')
        Api()
        logger.warning("Consumer is dead killing worker and process",
                       exc_info=True)
        atexit.register(quit_gracefully)
    except Exception as e:
        logger.error(str(e),
                     exc_info=True)
        atexit.register(quit_gracefully)
        logger.info('SHUTTING DOWN')

def __event_consumer__():
    try:
        logger.info('*********** Starting consumer ************')
        Consume()
        logger.warning("Consumer is dead killing worker and process",
                       exc_info=True)
        atexit.register(quit_gracefully)
    except Exception as e:
        logger.error(str(e),
                     exc_info=True)
        atexit.register(quit_gracefully)
        logger.info('SHUTTING DOWN')



def __main__():
    try:
        thread = threading.Thread(target=s3_api)
        thread.daemon = False
        thread.start()
        logger.info('consumer joining')
        __event_consumer__()
    except KeyboardInterrupt as e:
        logger.error(str(e),
                     exc_info=True)
        logger.info('SHUTTING DOWN')
        # thread.join()



if __name__ == '__main__':
    __main__()

