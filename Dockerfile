FROM python:3.7-slim AS compile-image
RUN apt-get update &&  apt-get install -y --no-install-recommends git build-essential gcc autoconf libtool automake
RUN python -m venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN mkdir s3io
COPY /s3_io s3io/s3_io
COPY setup.py s3io/setup.py
RUN pip install uwsgi &&\
   pip install git+https://github.com/violetina/chassis.py.git &&\
   cd s3io &&\
   python setup.py install

FROM python:3.7-slim AS run-image
COPY --from=compile-image /opt/venv /opt/venv
# set timezone
ENV TZ=Europe/Brussels
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
#VOLUME /home/app/.ssh

# add app data disabled, Optional
# COPY ./s3_io ./s3io/s3_io
COPY ./config.yml.docker ./config.yml
# copy config for tests
# todo add test stage
COPY ./tests ./tests
COPY ./config.yml.docker ./tests/config.yml
#todo volulme for test results injenkins
# VOLUME
# envs in openshift from secret so no need for this
#COPY ./.env ./.env
#COPY ./source_env.sh /app/source_env.sh

#RUN apt-get update &&  apt-get install -y --no-install-recommends openssh-client nano && apt-get clean && apt-get autoclean 
# add user guid and useruid
ARG GUID=1000
RUN groupadd -g $GUID -r app && useradd -m -u $GUID -b /home -r -g app app
COPY ./s3_io/api/ ./api
RUN chown app:app /opt && chmod g+wx /opt
RUN chown -R app:0 /app && chmod -R g+rwx /app 
#    chown -R app:0 /home/app/.ssh && chmod -R g+rwx /home/app/.ssh
USER app
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
ENV testval=123456
ENV RAB_PUB_USER=user
ENV RAB_PUB_PASSWORD=password
ENV RAB_PUB_HOST=a.domain.org
ENV REMOTECURL_PRIV_KEY_PATH=/home/USER/.ssh/id_rsa 
ENV REMOTECURL_USER=user
ENV REMOTECURL_HOST=server.do.main.org
ENV REMOTECURL_DOMAIN_HEADER=s3.do.main.org
ENV REMOTECURL_PASSW=13654987741852369
ENV DOWNLCHUNCKS_DOMAIN=s3.domain.org
ENV CASTOR_SWARMURL=fileget.domain.org
ENV CASTOR_SWARMDOMAIN=s3.domain.org
ENV S3_TO_FTP_USER=user
ENV S3_TO_FTP_PASSOWRD=passxord
ENV S3_TO_FTP_SERVER=host.do.main
ENV S3_TO_FTP_ACCESS_KEY=1236549874125896
ENV S3_TO_FTP_SECRET_KEY=veryunsecret
ENV CELERY_RES_BACKEND=elasticsearch://eshost:9200/s3io/results
ENV CELERY_BROKER_URL=amqp://USER:PASSWORD@rabithost:5672/py_workers
ENV CONSUMER_URI=amqp://USER:PASSWORDA@rabbithost:5672/
COPY ./entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
#, "s3io-daemon"]
CMD s3io-worker
