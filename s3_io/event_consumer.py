#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:40:19 2020
    Description:

         - queue : hardcodes atm to : s3_to_remotefs

    Args:
         - body: json
         - headers: "x-meemoo-request-id" required!

@author: tina
"""
from sys import exit
import pika
import json
import configparser
from  json import JSONDecodeError
from retry import retry
from viaa.observability import logging
from viaa.configuration import ConfigParser
from s3_io.create_url_to_filesystem_task import process
config = ConfigParser()
config_ = configparser.ConfigParser()
config_.read('/etc/viaa-workers/config.ini')
swarmurl = config_['castor']['swarmurl']
logger = logging.get_logger('s3io', config)


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

         - queue : hardcodes atm to : s3_to_remotefs

    Args:

         - body: json

         - headers: "x-meemoo-request-id" required!

    """
    url = config_['RabCon']['uri']
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()  # start a channel
    q = 's3_to_remotefs'
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue=q, durable=True)



    def callback(ch, method, properties, body):
        """
        the actual callback on message
         - Decodes rhe msg from json to dict
         - pass dict it to process function which starts a async job
        """

        # Process the body
        try:
            body = json.loads(body.decode('utf-8'))
            request_id = properties.headers["x-meemoo-request-id"]
            body["x-meemoo-request-id"] = request_id
            process(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            log_fields = {'x-meemoo-request-id': str(request_id)}
            logger.info('ACK valide msg x-meemoo-request-id: %s',
                        request_id,
                        fields=log_fields)
        except KeyError as e:
            logger.error('missing key: %s',
                         str(e), exc_info=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except JSONDecodeError as j_e:
            logger.error('Input Json error: %s',
                         str(j_e),
                         exc_info=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except pika.exceptions.ConnectionClosedByBroker:
            exit(1)

    try:
        channel.basic_consume(q, callback, consumer_tag='s3tofilesystem')
        # start consuming (blocks)
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.error('______got exit_________ ')
        channel.stop_consuming()
        channel.close()
        connection.close()
        exit


if __name__ == "__main__":
    logger.info('... sTARTING Consumer')
    __main__()
