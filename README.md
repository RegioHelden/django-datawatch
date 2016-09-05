[![PyPI version](https://badge.fury.io/py/django_datawatch.svg)](https://badge.fury.io/py/django_datawatch)

Django Datawatch
================
With Django Datawatch you are able to implement arbitrary checks on data, review their status and even describe what to do to resolve them.

Installation
------------

```shell
$ pip install django-datawatch
```

Add `django_datawatch` to your `INSTALLED_APPS`

Define a check:
---------------
Create `checks.py` inside your module.

```python
from django_datawatch.monitoring import monitor
from django_datawatch.base import BaseCheck
from django_datawatch.models import Result


@monitor.register
class CheckTime(BaseCheck):
    run_every = relativedelta(minute=1)  # scheduler will execute this check every 1 minute

    def generate(self):
        yield datetime.datetime.now()

    def check(self, payload):
        if payload.hour <= 7:
            return Result.STATUS.ok
        elif payload.hour <= 12:
            return Result.STATUS.warning
        return Result.STATUS.critical

    def get_identifier(self, payload):
        # payload will be our datetime object that we are getting from generate method
        return payload

    def get_payload(self, identifier):
        # as get_identifier returns the object we don't need to process it
        # we can return identifier directly
        return identifier
```

manage.py commands.
---------------------
Execute all checks
```shell
$ ./manage.py monitoring_run_checks
```

Settings
--------
```python
DJANGO_DATAWATCH = {
    'QUEUE_NAME': 'django_datawatch'
}
```

Improve Django Datawatch
-------------------------

We've included an example app to show how django_datawatch works and to make it easy to improve it.
Start by launching the included vagrant machine:
```bash
vagrant up
vagrant ssh
```

Then setup the example app environment:
```bash
./manage.py migrate
./manage.py loaddata example
```
The installed superuser is "example" with password "datawatch".

Run the development webserver:
```bash
./manage.py runserver 0.0.0.0:8000
```

Login on the admin interface and open http://ddw.dev:8000/ afterwards.
You'll be prompted with an empty dashboard. That's because we didn't run any checks yet.
Let's enqueue an update:
```bash
./manage.py monitoring_run_checks
```

Now we need to start a celery worker to handle the updates:
```bash
celery worker -A example -l DEBUG -Q django_datawatch
```

You will see some failed check now after you refreshed the dashboard view.

![Django Datawatch dashboard](http://static.jensnistler.de/django_datawatch.png "Django Datawatch dashboard")
