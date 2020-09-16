#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 8 09:07:08 2018

@author: tina
"""

from setuptools import setup

setup(name='s3_io',
      version='1.1.4',
      description='VIAA S3 Events',
      long_description='Publiseh s3 event to rabbitmq.',
      classifiers=[
          'Development Status :: 0.1-rc1',
          'Intended Audience :: Developers',
          'License :: MIT 2019 VIAA',
          'Programming Language :: Python :: 3.5',
          'Topic :: S3',
      ],
      keywords='S3 events',
      author='Tina Cochet',
      author_email='tina.cochet@viaa.be',
      license='MIT 2019 VIAA',
      packages=['s3_io'],
      package_dir={'s3_io': 's3_io'},
      package_data={
          's3_io': ['./api/*.yaml'],
      },
      install_requires=[
          'pika==1.1.0',
          'requests',
          'boto3==1.10.4',
          'python_logging_rabbitmq==2.0.0',
          'urllib3==1.24.3',
          'retry==0.9.2',
          'celery==4.3.0',
          'tqdm==4.36.1',
          'mako',
          'vine==1.3.0',
          'markdown >= 3.0',
          'paramiko==2.7.1',
          'elastic-apm==5.4.3',
          'connexion==2.6.0',
          'pytest-cov',
          'flake8==3.8.3',
          'flake8-junit-report==2.1.0',
          'elasticsearch==6.4.0',
      ],
      entry_points={
          'console_scripts': ['s3io-worker=s3_io.s3io_worker:__main__',
                              's3io-consumer=s3_io.event_consumer:__main__']},
      include_package_data=True,
      zip_safe=False)
