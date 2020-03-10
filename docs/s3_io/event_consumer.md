# Event Consumer

> Auto-generated documentation for [s3_io.event_consumer](../../s3_io/event_consumer.py) module.

Created on Fri Jan 10 15:40:19 2020

- [S3io](../README.md#s3io) / [Modules](../MODULES.md#s3io-modules) / [S3 Io](index.md#s3-io) / Event Consumer

Description:

- queue : hardcodes atm to : s3_to_remotefs

#### Arguments

- `-` *body* - json

- `-` *headers* - "x-meemoo-request-id" required!

- `@author` - tina

#### Attributes

- `logger` - config_.read('/etc/viaa-workers/config.ini')
  swarmurl = config_['castor']['swarmurl']: `logging.get_logger('s3io', config)`
