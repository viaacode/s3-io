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
#ELASTIC_APM_USE_STRUCTLOG=True

from s3_io.s3io_tasks import app
import configparser
from s3_io.event_consumer import __main__ as Consume 
from viaa.observability import logging
from viaa.configuration import ConfigParser
import threading
import atexit
from python_logging_rabbitmq import RabbitMQHandlerOneWay
from celery.signals import after_setup_task_logger, setup_logging, after_setup_logger,task_postrun,task_prerun, celeryd_after_setup
config = ConfigParser()
from celery.result import AsyncResult
config_ = configparser.ConfigParser()
config_.read('/etc/viaa-workers/config.ini')
rabbit = RabbitMQHandlerOneWay(host=config_['RabPub']['host'], 
                                    username=config_['RabPub']['user'],
                                    password=config_['RabPub']['passw'],
                                    fields_under_root=True,
                                    port=5672)
logger = logging.get_logger('s3io', config)


# from elasticapm import Client, instrument
# from elasticapm.contrib.celery import register_exception_tracking, register_instrumentation
# import elasticapm
# #elasticapm.instrument()
# elasticapm.set_transaction_name('S3IO')
# elasticapm.set_transaction_result('SUCCESS')


def add_rabbithandler():
    logger = logging.get_logger('s3io', config)
    if 'RabbitMQHandlerOneWay' not in logger.handlers:
        logger.addHandler(rabbit)


@task_postrun.connect
def log_task_complete(sender, task_id, task, args, kwargs, **_kwargs):
    try:
        #add_rabbithandler()
        result = AsyncResult(task_id).result      
        if result is None:
            result = 'NO_RESULT_FOUND'
    except Exception as e:
        logger.error(str(e),exc_info=True)
    
   


@task_prerun.connect
def log_task_Started(sender, task_id, task, args, kwargs, **_kwargs):   
    try:
        add_rabbithandler()
    
        fields={
                'celery_task_id':task_id,
                'celery_task_name':str(task),
                 'x-viaa-request-id': task_id
                }
        logger.info("prerun task: %s task_id: %s ",str(task),str(task_id),
                    fields=fields)
    except Exception as e:
        logger.error("error adding handler : %s/",str(e),exc_info=True)




# @celeryd_after_setup.connect
# def setup_meemoo_logging(sender, instance, conf, **kwargs):
#     logger = logging.get_logger('s3io', config)

#     try:
#         add_rabbithandler()
#     except Exception as e:
#         logger.error("error adding handler :/",exc_info=True)

    
# to mess celery log you need this below
@setup_logging.connect
def on_celery_setup_logging(**kwargs):
    pass


def quit_gracefully(t=None):
    logger.warning("######### sending app.control.shutdown() DISABLED#########")
    # a=app.control.shutdown()
    # print(a)
    a='ERROR'
    ## todo send signal TERM
    #worker_process_shutdown
    logger.warning('######### Bye, this is it i am Quiting ######### %s',a)
    if t is not None:
        try:
            logger.warning("KILLING thread!")
            t.join()
            exit(0)
        except Exception as e:
            logger.error(str(e),exc_info=True)
    else:
        exit(0)


def __event_consumer__():
    try:
        logger.info('*********** Starting consumer ************')
        Consume()
        logger.warning("Consumer is dead killing worker and process",
                       exc_info=True)
        atexit.register(quit_gracefully)
    except Exception as e:
        logger.error(str(e),exc_info=True)
        atexit.register(quit_gracefully)
        logger.info('SHUTTING DOWN')
        
def worker():
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
        exit(1)
    exit(0)
  
   
def __main__():
    # client = Client({'SERVICE_NAME': 'S3IO',
    #              'DEBUG': False,
    #              'ELASTIC_APM_BREAKDOWN_METRICS':False,
    #              'SERVER_URL': 'http://apm-server-prd.apps.do-prd-okp-m0.do.viaa.be:80'} )
    # elasticapm.instrument()
    # register_exception_tracking(client)
    # register_instrumentation(client)
    try:
        thread = threading.Thread(target=worker)
        thread.daemon = False
        thread.start()
        logger.info('consumer joining')
        __event_consumer__()
    except KeyboardInterrupt as e:
        logger.error(str(e),exc_info=True)
        logger.info('SHUTTING DOWN')
        #thread.join()
        atexit.register(quit_gracefully,t=thread)

    
if __name__ == '__main__':
  __main__()
   