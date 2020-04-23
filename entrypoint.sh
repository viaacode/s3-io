#!/bin/bash
if [ "${1}" == 's3io-daemon' ];then
	s3io-worker

elif [ "${1}" == 's3io-daemon-local' ];then
	echo sourcing ENV from .env
        . .env &&
        s3io-worker

fi
exec "$@"
