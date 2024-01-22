Changelog
=========

Unreleased
------------------


4.0.0 (2024-01-22)
------------------

- BREAKING: added the ability to assign multiple users and groups instead of just one

3.6.0 (2023-06-12)
------------------

- Show current config settings in superuser debug table
- Add screenshot of details page to README
- use db_alias if provided on post_save signals, Thanks @stefan-cardnell-rh

3.5.0 (2023-04-20)
------------------

- Add support for Python 3.11 and Django 4.2
- Update example app to bootstrap 5
- Upgrade libraries in test environment
- Update README to reflect Docker Compose plugin

3.4.0 (2023-04-19)
------------------

- Add task datawatch_cleanup for cleaning up ghost Results
- Update delete_results signal handler to use db_alias if provided
- Update celery commands in README

3.3.0 (2023-01-02)
------------------

- Remove unnecessary compatibility code for Python 2.x and Python < 3.3
- Use time-machine instead of freezegun in tests
- Upgrade libraries in test environment
- Add tests and support for Django 4.1

3.2.0 (2022-10-07)
------------------

- Add tests and support for Django 4.0 (Django 4.1 is still blocked by [django-celery-beat](https://github.com/celery/django-celery-beat/pull/567))

3.1.0 (2022-08-23)
------------------

- Make dispatch_uid of the signal receivers registered by datawatch unique

3.0.2 (2022-05-18)
------------------

- fix pypi publish to use an api token instead of a password

3.0.1 (2022-05-18)
------------------

- Add support for trigger update resolver methods to return multiple payloads
- Fixed a bug with lambdas that prevented all checks to be refreshed on trigger updates

3.0.0 (2022-01-25)
------------------

- Upgrade packages
- BREAKING CHANGE! Remove Python <3.8 support, remove Django <3.2 support
- BREAKING CHANGE! Dependency minimum versions increased

2.4.3 (2021-08-27)
------------------
- Fix condition that skips the check if there's no payload

2.4.2 (2021-08-24)
------------------
- Pin psycopg2 to 2.8.6 in test depedencies for Django 2.2 compatibility

2.4.1 (2021-08-24)
------------------
- Fix test case
- Renovate test environment

2.4.0 (2021-08-24)
------------------
- Added 'modified' and 'created' as readonly fields to the admin for Result model [Jens Nistler]
- Update of related datasets wrapped in a transaction commit handler to make sure data is written before the update handler gets executed [Jens Nistler]

2.3.4 (2021-05-18)
------------------

- Fix user_forced_refresh in celery backend (wasn't properly handed over to synchronous backend)

2.3.3 (2021-03-18)
------------------

- Don't use ugettext* anymore as Python 3 is always unicode compatible, replace by gettext*

2.3.2 (2021-03-18)
------------------

- Fix celery backend not forwarding the user_forced_refresh flag #50

2.3.1 (2021-03-17)
------------------

- Pass payload to user_forced_refresh_hook #50

2.3.0 (2021-03-17)
------------------

- Add code hook that gets executed when an update is forced by a user from the web view #50

2.2.5 (2021-02-01)
------------------

- properly handle empty generators (yield None)

2.2.4 (2020-11-16)
------------------

- remove Python 3.6 compatibility
- fix build status report in README

2.2.3 (2020-11-16)
------------------

- fix Django 2.2 requirement issue

2.2.2 (2020-10-08)
------------------

- this only to validate github actions publish to pypi

2.2.1 (2020-10-08)
------------------

- fix and update build environment and dependencies

2.2.0 (2020-10-07)
------------------

- Allow extending acknowledgements #47
- Handle exception during acknowledgment #48

2.1.1 (2020-04-23)
------------------

- Linting fixes

2.1.0 (2020-04-23)
------------------

- Revert example app check execution to be synchronous #43
- Remove dependency to docker-hostmanager #44
- Add optional superuser debug info to detail view #45

2.0.0 (2019-11-04)
------------------

- Upgrade packages
- BREAKING CHANGE! Remove Python 2.x support

1.1.2 (2019-08-02)
------------------

- Update changelog and documentation to match patch 1.1.1

1.1.1 (2019-006-08)
------------------

- BREAKING CHANGE! Renamed datawatch_delete_ghost_results management comand to datawatch_clean_up since it's now also deleting ghost executions [Kseniya Potter]

1.0.3 (2019-03-20)
------------------

- Fix celery timezone issue [Leonardo Antunes]

1.0.2 (2019-02-14)
------------------

- Fix accidently bumped version of bootstrap3, bad bumpversion... [Jens Nistler]


1.0.1 (2019-02-14)
------------------

- Set readme to be interpreted as markdown [Jens Nistler]


1.0.0 (2019-02-13)
------------------

- BREAKING CHANGE! switch to celery 4, you now have to add the scheduler task to your CELERYBEAT_SCHEDULE, details in README.md [Jens Nistler]
- BREAKING CHANGE! removed DJANGO_DATAWATCH_CELERY_QUEUE_NAME setting, use task routing instead, see http://docs.celeryproject.org/en/latest/userguide/routing.html [Jens Nistler]
- Update dependencies [Jens Nistler]
- It's time for a 1.0.0 release since datawatch is used internally at RegioHelden for over two years now [Jens Nistler]


0.3.1 (2018-08-07)
------------------

- BREAKING CHANGE! Switch from relativedelta to celerys crontab for run_every defintions [Jens Nistler]


0.2.8 (2018-08-07)
------------------
- Add missing migration from 0.2.7 [Jens Nistler]
- Switch from vagrant to docker for test environment [Jens Nistler]


0.2.7 (2018-08-07)
------------------
- Drop Django 1.9 from CI tests [Steffen Zieger]
- Add Django 2.1 to CI tests [Steffen Zieger]
- Add deployment to travis config [Steffen Zieger]
- Use bumpversion for new releases [Steffen Zieger]
- Fixes for Django 2.1 support [Steffen Zieger]


0.2.6 (2018-08-07)
------------------
- Fix scheduler [Steffen Zieger]


0.2.5 (2018-02-16)
------------------
- Handle and log exceptions during post_save of datawatch to not break the
business logic of the main application using datawatch #37 [Jens Nistler]


0.2.4 (2018-01-30)
------------------
- Add new release. [Vladimir Potter]
- Set max value to 365 for `days` field in AcknowledgeForm. [Vladimir Potter]


0.2.3 (2018-01-02)
------------------
- Add new release. [Mounir Messelmeni]
- Fix wrong fields names. [Mounir Messelmeni]
- Adding coverage badge. [Mounir]
- Adding support for coveralls integration with travisci (#35) [Mounir]

  Adding support for coveralls integration with travisci
- Merge pull request #34 from
  RegioHelden/test_against_different_django_versions. [Mounir]

  Test against different django versions
- Fix error with python 3.5 in testing. [Mounir Messelmeni]
- Make travis test against different django version and newer python
  version. [Mounir Messelmeni]
- Add more badges. [Mounir]
- Fixing pypi badge. [Mounir]
- Updating changelog. [Mounir Messelmeni]


0.2.1 (2017-02-23)
------------------
- Adding new release. [Mounir Messelmeni]
- Adding slug and group filtering for results. [Mounir Messelmeni]
- Removing django-braces dependency and use builtin Django mixins.
  [Mounir Messelmeni]
- Updating changelog. [Mounir]
- Adding changelog. [Mounir]
- Adding missing vagrant plugins. [Mounir]
- Fix broken example for datetime. [Mounir]
- Test on python 3.4 as used in the vm. [Jens Nistler]
- Update translations, refs #27. [Jens Nistler]


0.2.0 (2016-11-21)
------------------
- Remove all wordings of monitoring and replace by datawatch, fixes #27.
  [Jens Nistler]
- Make all checks model based, refs #26. [Jens Nistler]
- Catch does not exist for deleted models, refs #26. [Jens Nistler]
- Delete results of deleted model instances, closes #26. [Jens Nistler]
- Fix celery refresh task, fixes #25. [Jens Nistler]
- Support batch refreshing check results, release 0.1.21, fixes #25.
  [Jens Nistler]
- Release 0.1.20. [Jens Nistler]
- Redirect to index instead of 404 if check result does not exist
  (anymore), fixes #24. [Jens Nistler]
- Use synchronous backend in example app, fixes #23. [Jens Nistler]
- Extend run command to support running a single check, release 0.1.19,
  fixes #22. [Jens Nistler]
- Add command to list all registered checks, refs #22. [Jens Nistler]
- Format description and result data, closes #21. [Jens Nistler]


0.1.18 (2016-10-25)
-------------------
- Change config, add tests for trigger_update deactivation, refs #8.
  [Jens Nistler]
- Release 0.1.17, refs #20. [Jens Nistler]
- Fix scheduler, add tests for scheduler, refs #20. [Jens Nistler]
- Use scheduler to run periodic celery task, release 0.1.16, fixes #20.
  [Jens Nistler]
- Document settings. [Jens Nistler]
- Release 0.1.15. [Jens Nistler]
- Disable post save signal during tests and option to force it, fixes
  #19. [Jens Nistler]
- Reset migrations to prevent issues with renamed model, closes #18.
  [Jens Nistler]
- Update README.md. [Jens Nistler]
- Allow skipping checks and deleting results, closes #17. [Jens Nistler]
- Make generate function optional, closes #16. [Jens Nistler]
- Update post_save handler, refs #15. [Jens Nistler]
- Hide config link if no config defined, fixes #12. [Jens Nistler]


0.1.11 (2016-09-30)
-------------------
- Release 0.1.11. [Bogdan Radko]
- Release 0.1.10. [Bogdan Radko]
- Scheduler needs to run on check instances. [shofinetz]

  Received error:
- Fix 'acknowledge' permission naming. [shofinetz]

  Use the permission defined in the Result class
- Set default for jsonfield to not clash with older django extension
  versions, release 0.1.9. [Jens Nistler]
- Release 0.1.8. [Jens Nistler]
- Run scheduler every minute. [Jens Nistler]
- Execution backends extracted, fixes #2. [Jens Nistler]
- Update badges in readme. [Jens Nistler]
- Add python3 virtualenv, fix unittests for python3, refs #8. [Jens
  Nistler]
- Update travis ci database usage, refs #8. [Jens Nistler]
- Update readme. [Jens Nistler]
- Fix travis ci badge, refs #8. [Jens Nistler]
- Run tests on travis ci, refs #8. [Jens Nistler]
- Add integration test to check if all required methods are implemented
  on user defined checks, refs #8. [Jens Nistler]
- Optionally limit maximum days to acknowledge per check, fixes #9.
  [Jens Nistler]
- Add check select to dashboard filter form, fixes #7. [Jens Nistler]
- Handle permissions and check them in the template, fixes #1. [Jens
  Nistler]
- Adjust documentation for check response class, refs #10. [Jens
  Nistler]
- Return response object from check, refs #10. [Jens Nistler]
- Fix session form handling, bump to 0.1.7. [Jens Nistler]
- Added not committed files for ghost results deletion. [Bogdan Radko]
- Release 0.1.6. [Jens Nistler]


0.1.6 (2016-09-04)
------------------
- Use filtered queryset to calculate stats, allow blank on nullable
  fields. [Jens Nistler]
- Added manage.py command to delete ghost results. [Bogdan Radko]


0.1.5 (2016-09-04)
------------------
- Release 0.1.5. [Jens Nistler]
- Remember dashboard form data in session. [Jens Nistler]
- Rename model "Check" to "Result" [Bogdan Radko]
- Updated readme file. Scheduler is now able to run checks with not
  defined 'run_every' attribute. [Bogdan Radko]


0.1.4 (2016-09-04)
------------------
- Rename danger to critical, fix scheduler, include django-bootstrap in
  bundle to fix the default templates. [Jens Nistler]
- Changed message text at example/dashboard.html when there are no
  checks found. [Bogdan Radko]
- Added anchors to example/dashboard.html. [Bogdan Radko]


0.1.3 (2016-09-04)
------------------
- Include templates and locales in bundle. [Jens Nistler]


0.1.2 (2016-09-04)
------------------
- Include subpackages in bundle. [Jens Nistler]


0.1.1 (2016-09-04)
------------------
- Release 0.1.1. [Jens Nistler]
- Added settings functionality. Added "QUEUE_NAME" default setting.
  BaseCheck.handle method refactoring. [Bogdan Radko]
- Add pypi badge to readme. [Jens Nistler]
- Add execution scheduler. [Jens Nistler]
- Improve example dataset. [Jens Nistler]


0.1.0 (2016-09-04)
------------------
- Rename application to django_datawatch. [Jens Nistler]
- Update setup.cfg. [Jens Nistler]
- Add monitoring and example app. [Jens Nistler]
- Preparing for PyPI. Vagrant setup for development. [Bogdan Radko]



