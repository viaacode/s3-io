#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:40:19 2020

@author: tina
"""
from sys import exit

import pika
import json
import configparser
from retry import retry
from viaa.observability import logging
from viaa.configuration import ConfigParser
from s3io.create_url_to_filesystem_task import process
config = ConfigParser()
config_ = configparser.ConfigParser()
config_.read('/etc/viaa-workers/config.ini')
swarmurl = config_['castor']['swarmurl']
logger = logging.get_logger('s3io', config)



# from elasticapm import Client
import elasticapm
elasticapm.instrument()
elasticapm.set_transaction_name('S3IO')
elasticapm.set_transaction_result('SUCCESS')
#from elasticapm.handlers.logging import LoggingHandler
# client = Client({'SERVICE_NAME': 'S3IO',
#                  'DEBUG': False,
#                  'SERVER_URL': 'http://apm-server-prd.apps.do-prd-okp-m0.do.viaa.be:80'} ) 
# 
@retry(pika.exceptions.AMQPConnectionError,
       delay=5,
       tries=-1,
       backoff=2,
       jitter=(1, 3))
def __main__():
    url = config_['RabCon']['uri']
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel() # start a channel

    
    q = 's3_to_remotefs'
    channel.basic_qos(prefetch_count=2)
    channel.queue_declare(queue=q, durable=True)
    try:
        # create a function which is called on incoming messages
         
         def callback(ch, method, properties, body):
              body=json.loads(body.decode('utf-8'))
              #client.begin_transaction(transaction_type='request')
              #client.capture_message('Start Process AMQP msg'  )   
              request_id = properties.headers["x-meemoo-request-id"]
              log_fields={'x-meemoo-request-id': str(request_id)}
              logger.info('About to validate msg x-meemoo-request-id: %s',
                          request_id,
                          fields=log_fields)
              # Process the body
              try:
                   body["x-meemoo-request-id"] = request_id
                   process(body)
              except ValueError as e:
                   logger.error(str(e),exc_info=True)
                   ch.basic_nack(delivery_tag=method.delivery_tag)
               #    client.capture_exception()
                   channel.stop_consuming()
                   connection.close()
                #   client.end_transaction('pika_amqp', 500)
             
              #client.end_transaction('pika_amqp', 200)
             
              ch.basic_ack(delivery_tag=method.delivery_tag)

         channel.basic_consume(q, callback, consumer_tag='s3tofilesystem')
         # start consuming (blocks)
         channel.start_consuming()

    except KeyboardInterrupt:
        #client.capture_exception()
        channel.stop_consuming()
        connection.close()
        exit(0)
    #except pika.exceptions.ConnectionClosedByBroker:
        # Uncomment this to make the example not attempt recovery
        # from server-initiated connection closure, including
        # when the node is stopped cleanly
    except pika.exceptions.ConnectionClosedByBroker:
        exit(1)
if __name__ == "__main__":
           
    # handler = LoggingHandler(client=client)
    # logging.get_logger('elasticapm').setLevel('INFO')
    # logger.addHandler(handler)
    logger.info('... sTARTING dAEMON')
    
    __main__()

