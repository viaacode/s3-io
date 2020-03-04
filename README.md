# s3_events.s3_events

Created on Thu Dec 19 10:05:23 2019

@author: tina

## s3-events
```console
#cli: s3-events
```
Description:

- Starts the listener on s3_io queue
- Console script
- Creates a Celery Task to move the file to ingest sace

Args:

- None

### Setup
```python
python setup.py install 
```
Description:

- install the package


### Config
```python
#file: /etc/viaa-workers/config.ini 
```
Description:

- all the s€crt$tuff is in there
- consult file config.dist for info and rename 

### Docs
```pydocmd
pydocmd build
```
Description:

- Builds the documentation


## Makefile info
```
#cli: make all
```
Description:

- Installs package and the documentation

```
#cli: make docs
```
Description:

- build and serve documentation

```
#cli: make clean
```
Description:

- cleans cwd and uninstalls package

### System Daemon
```pydocmd
#cli: systemctl start s3-events
```
Description:

- Systemd daemon 

## Tips
```
pydocmd serve
```
Description:

- will server the documentation