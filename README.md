[![PyPI version](https://badge.fury.io/py/django_datawatch.svg)](https://pypi.python.org/pypi/django-datawatch)
[![Travis CI build status](https://travis-ci.org/RegioHelden/django-datawatch.svg)](https://travis-ci.org/RegioHelden/django-datawatch)

# Django Datawatch

With Django Datawatch you are able to implement arbitrary checks on data, review their status and even describe what to do to resolve them.
Think of [nagios](https://www.nagios.org/)/[icinga](https://www.icinga.org/) for data.

## Requirements

Currently celery is required to run the checks. We'll be supporting different backends in the future.

## Install

```shell
$ pip install django-datawatch
```

Add `django_datawatch` to your `INSTALLED_APPS`

## Write a custom check

Create `checks.py` inside your module.

```python
from datetime import datetime

from dateutil.relativedelta import relativedelta

from django_datawatch.datawatch import datawatch
from django_datawatch.base import BaseCheck, CheckResponse
from django_datawatch.models import Result


@datawatch.register
class CheckTime(BaseCheck):
    run_every = relativedelta(minute=5)  # scheduler will execute this check every 5 minutes

    def generate(self):
        yield datetime.now()

    def check(self, payload):
        response = CheckResponse()
        if payload.hour <= 7:
            response.set_status(Result.STATUS.ok)
        elif payload.hour <= 12:
            response.set_status(Result.STATUS.warning)
        else:
            response.set_status(Result.STATUS.critical)
        return response

    def get_identifier(self, payload):
        # payload will be our datetime object that we are getting from generate method
        return payload

    def get_payload(self, identifier):
        # as get_identifier returns the object we don't need to process it
        # we can return identifier directly
        return identifier
```



### generate

Must yield payloads to be checked. The check method will then be called for every payload.

### check

Must return an instance of CheckResponse.

### get_identifier

Must return a unique identifier for the payload. 

## Run your checks

A management command is provided to queue the execution of all checks based on their schedule.
Add a crontab to run this command every minute and it will check if there's something to do.

```shell
$ ./manage.py datawatch_run_checks
$ ./manage.py datawatch_run_checks --slug=example.checks.UserHasEnoughBalance
```

## Refresh your check results

A management command is provided to forcefully refresh all existing results for a check.
This comes in handy if you changes the logic of your check and don't want to wait until the periodic execution or an update trigger.

```shell
$ ./manage.py datawatch_refresh_results
$ ./manage.py datawatch_refresh_results --slug=example.checks.UserHasEnoughBalance
```

## Get a list of registered checks

```shell
$ ./manage.py datawatch_list_checks
```

## Clean up your database

Remove the unnecessary check results if you've removed the code for a check.

```shell
$ ./manage.py datawatch_delete_ghost_results
```

## Settings

```python
DJANGO_DATAWATCH_BACKEND = 'django_datawatch.backends.synchronous'
DJANGO_DATAWATCH_CELERY_QUEUE_NAME = 'django_datawatch'
DJANGO_DATAWATCH_RUN_SIGNALS = True
```

### DJANGO_DATAWATCH_BACKEND

You can chose the backend to run the tasks. Supported are 'django_datawatch.backends.synchronous' and 'django_datawatch.backends.celery'.

Default: 'django_datawatch.backends.synchronous'

### DJANGO_DATAWATCH_CELERY_QUEUE_NAME

You can customize the celery queue name for async tasks (applies only if celery backend chosen).

Default: 'django_datawatch'

### DJANGO_DATAWATCH_RUN_SIGNALS

Use this setting to disable running post_save updates during unittests if required.

Default: True

# CONTRIBUTE

We've included an example app to show how django_datawatch works.
Start by launching the included vagrant machine.
```bash
vagrant plugin install vagrant-hostmanager
vagrant plugin install vagrant-vbguest
vagrant up
vagrant ssh
```

Then setup the example app environment.
```bash
./manage.py migrate
./manage.py loaddata example
```
The installed superuser is "example" with password "datawatch".

Run the development webserver.
```bash
./manage.py runserver 0.0.0.0:8000
```

Login on the admin interface and open http://ddw.dev:8000/ afterwards.
You'll be prompted with an empty dashboard. That's because we didn't run any checks yet.
Let's enqueue an update.
```bash
./manage.py datawatch_run_checks --force
```

The checks for the example app are run synchronously and should be updated immediately.
If you decide to switch to the celery backend, you should now start a celery worker to process the checks.
```bash
celery worker -A example -l DEBUG -Q django_datawatch
```

You will see some failed check now after you refreshed the dashboard view.

![Django Datawatch dashboard](http://static.jensnistler.de/django_datawatch.png "Django Datawatch dashboard")
