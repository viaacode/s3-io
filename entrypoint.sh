#!/bin/bash
if [ "${1}" == 's3io-daemon' ];then
	. .env &&
	s3io-worker
elif [ "${1}" == 'consumer' ];then
        . .env &&

	s3io-consumer
else
	. .env &&
	/bin/bash
fi


