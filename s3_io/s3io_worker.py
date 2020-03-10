#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 11:58:05 2019

- Description:

    - Start Celery worker from cli
    - set concurrency here

- Kind:

    - entrypoint

@author: tina
"""

import sys
import threading
import atexit
from s3_io.event_consumer import __main__ as Consume
from s3_io.s3io_tasks import app
from viaa.observability import logging
from viaa.configuration import ConfigParser
from python_logging_rabbitmq import RabbitMQHandlerOneWay
from celery.signals import setup_logging, task_postrun, task_prerun
from celery.result import AsyncResult
config = ConfigParser()
import pprint
pprint.pprint(config.config['test'])
rabbit = RabbitMQHandlerOneWay(
     host=config.config['logging']['RabPub']['host'],
     username=config.config['logging']['RabPub']['user'],
     password=config.config['logging']['RabPub']['passw'],
     fields_under_root=True,
     port=5672)
logger = logging.get_logger('s3io', config)




def add_rabbithandler():
    """ADD a log handle to get task results in log"""
    _logger = logging.get_logger('s3io', config)
    if 'RabbitMQHandlerOneWay' not in logger.handlers:
        _logger.addHandler(rabbit)


@task_postrun.connect
def log_task_complete(sender, task_id, task, args,  **kwargs):
    """Runs on task complete """
    # add_rabbithandler()
    result = AsyncResult(task_id).result
    if result is None:
        result = 'NO_RESULT_FOUND'


@task_prerun.connect
def log_task_Started(sender, task_id, task, args, **kwargs):
    """RUNS ON TASK START"""
    try:
        add_rabbithandler()
        fields = {
            'celery_task_id': task_id,
            'celery_task_name': str(task),
            'x-viaa-request-id': task_id}
        logger.info("prerun task: %s task_id: %s ",
                    str(task),
                    str(task_id),
                    fields=fields)
    except Exception as e:
        logger.error("error adding handler : %s/",
                     str(e),
                     exc_info=True)


# to mess celery log you need this below
@setup_logging.connect
def on_celery_setup_logging(**kwargs):
    """tO MESS WITH THE LOGGER"""
    pass
    # return True

def quit_gracefully(t=None):
    logger.warning("######### sending app.control.shutdown() DISABLED########")
    # a=app.control.shutdown()
    # print(a)
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

def worker():
    """sTARTS the celery worker THREAD"""
    argv = [
        'worker',
        '--loglevel=INFO',
        '-n=s3ior@%h',
        '--concurrency=2',
        '-E',
    ]
    logger.info("********* starting the worker ********* ")
    try:
        app.worker_main(argv)
    except KeyboardInterrupt:
        atexit.register(quit_gracefully)
        sys.exit(1)
    sys.exit(0)


def __main__():
    try:
        thread = threading.Thread(target=worker)
        thread.daemon = False
        thread.start()
        logger.info('consumer joining')
        __event_consumer__()
    except KeyboardInterrupt as e:
        logger.error(str(e),
                     exc_info=True)
        logger.info('SHUTTING DOWN')
        # thread.join()
        atexit.register(quit_gracefully,
                        t=thread)


if __name__ == '__main__':
    __main__()
