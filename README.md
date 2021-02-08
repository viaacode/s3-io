# s3io


@author: tina

## s3io
```console
#cli: s3-worker
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

-  see docs dir
- update with handsdown -d (while in root of git dir)

Description:

- Builds the documentation


