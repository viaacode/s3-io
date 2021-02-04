#!/bin/bash
set e
celery inspect ping -A s3_io.s3io_tasks | egrep OK | egrep $(hostname)  || echo ERROR & exit 1
