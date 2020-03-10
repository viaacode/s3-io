#!/bin/bash
if [ "${1}" == 's3io-daemon' ];then
	s3io-worker

elif [ "${1}" == 's3io-daemon-local'];then
	echo sourcing ENV from .env
        . .env &&
        s3io-worker

elif [ "${1}" == 'consumer' ];then
	s3io-consumer
else
	/bin/bash
fi


