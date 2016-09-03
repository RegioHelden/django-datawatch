Django Monitoring
=================
Extensive documentation will be provided soon.

Improve django_monitoring
-------------------------

We've included an example app to show how django_monitoring works and to make it easy to improve it.
Start by launching the included vagrant machine:
```bash
vagrant up
```

Then setup the example app environment:
```bash
./manage.py migrate
./manage.py loaddata example
```
The installed superuser is "example" with password "monitoring".

Run the development webserver:
```bash
./manage.py runserver 0.0.0.0:8000
```

Login on the admin interface and open http://dm.dev:8000/ afterwards.
You'll be prompted with an empty dashboard. That's because we didn't run any checks yet.
Let's enqueue an update:
```bash
./manage.py monitoring_run_checks
```

Now we need to start a celery worker to handle the updates:
```bash
celery worker -A example -l DEBUG -Q django_monitoring
```

You will see some failed check now after you refreshed the dashboard view.

![Django monitoring dashboard](http://static.jensnistler.de/django_monitoring.png "Django monitoring dashboard")
