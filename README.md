[![PyPI version](https://badge.fury.io/py/django_datawatch.svg)](https://pypi.python.org/pypi/django-datawatch)
[![Travis CI build status](https://travis-ci.org/RegioHelden/django-datawatch.svg)](https://travis-ci.org/RegioHelden/django-datawatch)

Django Datawatch
================
With Django Datawatch you are able to implement arbitrary checks on data, review their status and even describe what to do to resolve them.

Requirements
------------
Currently celery is required to run the checks. We'll be supporting different backends in the future.

Install
-------
```shell
$ pip install django-datawatch
```

Add `django_datawatch` to your `INSTALLED_APPS`

Write a custom check
--------------------
Create `checks.py` inside your module.

```python
from django_datawatch.monitoring import monitor
from django_datawatch.base import BaseCheck, CheckResponse
from django_datawatch.models import Result


@monitor.register
class CheckTime(BaseCheck):
    run_every = relativedelta(minute=5)  # scheduler will execute this check every 5 minutes

    def generate(self):
        yield datetime.datetime.now()

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

generate
~~~~~~~~
Must yield payloads to be checked. The check method will then be called for every payload.

check
~~~~~
Must return an instance of CheckResponse.

get_identifier
~~~~~~~~~~~~~~
Must return a unique identifier for the payload. 

Run your checks
---------------
A management command is provided to queue the execution of all checks based on their schedule.
Add a crontab to run this command every minute and it will check if there's something to do.

```shell
$ ./manage.py monitoring_run_checks
```

Settings
--------
You can customize the celery queue name for async tasks.

```python
DJANGO_DATAWATCH = {
    'QUEUE_NAME': 'django_datawatch'
}
```

CONTRIBUTE
----------

We've included an example app to show how django_datawatch works.
Start by launching the included vagrant machine.
```bash
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
./manage.py monitoring_run_checks
```

Now we need to start a celery worker to handle the updates.
```bash
celery worker -A example -l DEBUG -Q django_datawatch
```

You will see some failed check now after you refreshed the dashboard view.

![Django Datawatch dashboard](http://static.jensnistler.de/django_datawatch.png "Django Datawatch dashboard")
