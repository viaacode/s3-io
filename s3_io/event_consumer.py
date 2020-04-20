#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:40:19 2020

Description:

    - queue : hardcodes atm to : s3_to_remotefs

Args:

    - body: json

    - headers: "x-request-id" required!

@author: tina
"""
from sys import exit
import json
import uuid
import configparser
from json import JSONDecodeError
import pika
from retry import retry
from viaa.observability import logging#, correlation
from viaa.observability.correlation import CorrelationID
from viaa.configuration import ConfigParser
from s3_io.create_url_to_filesystem_task import process
config = ConfigParser()
config_ = configparser.ConfigParser()
logger = logging.get_logger('s3io', config)
swarmurl = config.app_cfg['castor']['swarmurl']

# todo use new feature ???
#correlation.initialize(flask=None, logger=logger, pika=pika, requests=None)





@retry(pika.exceptions.AMQPConnectionError,
       delay=5,
       tries=-1,
       backoff=2,
       jitter=(1, 3))
def __main__():
    """
    Description:

         - Cunsumes from rabbitMQ queue and creates a job,
         msg ack on async task create

         - prefetch 1 msg:

         - queue : incoming queue : s3_to_remotefs(might move to config)

    Args:

         - body: json

         - headers: "x-request-id" optional!

    """
    url = config.app_cfg['RabCon']['uri']
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()  # start a channel
    incoming_queue = 's3_to_remotefs'
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue=incoming_queue, durable=True)



    def callback(ch, method, properties, body):
        """
        Description:

            The actual callback on message

          - Decodes rhe msg from json to dict

          - pass dict it to process function to start a async job

          - Get current request_id to pass to other modules

        """

        # Process the body
        try:
            properties = pika.BasicProperties(
                delivery_mode=2,
                correlation_id=properties.correlation_id)
            body = json.loads(body.decode('utf-8'))
            #request_id = properties.headers.get("X-Correlation-ID")
            request_id = properties.correlation_id
            test_chas_corid = CorrelationID().correlation_id
            if request_id is None:
                request_id = uuid.uuid4().hex
                logger.info("Genrated a random request id")
            # enrich the body with request id to use in other modules
            body["x-request-id"] = request_id
            process(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            log_fields = {'x-request-id': str(request_id)}
            logger.info('ACK valide msg x-request-id: %s',
                        request_id,
                        fields=log_fields,
                        correlationId=request_id)
        except KeyError as k_e:
            logger.error('missing key: %s',
                         str(k_e), exc_info=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except JSONDecodeError as j_e:
            logger.error('Input Json error: %s',
                         str(j_e),
                         exc_info=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except pika.exceptions.ConnectionClosedByBroker:
            exit(1)

    try:
        channel.basic_consume(incoming_queue,
                              callback,
                              consumer_tag='s3tofilesystem')
        # start consuming (blocks)
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.warning('______Cunsumer exit_________')
        channel.stop_consuming()
        channel.close()
        connection.close()
        exit()


if __name__ == "__main__":
    logger.info('... sTARTING Consumer')
    __main__()
