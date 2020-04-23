# -*- coding: UTF-8 -*-
from os.path import join, dirname
from setuptools import setup, find_packages


def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return ''


setup(
    name='django-datawatch',
    packages=find_packages(exclude=['example*']),
    version='2.1.1',
    description='Django Datawatch runs automated data checks in your Django installation',
    author='Jens Nistler <opensource@jensnistler.de>, Bogdan Radko <bogdan.radko@regiohelden.de>',
    author_email='opensource@regiohelden.de',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    install_requires=[
        'celery>=3.1.25',
        'Django>=1.11.26',
        'django-bootstrap3>=11.0.0',
        'django-extensions>=2.1.5',
        'django-model-utils>=3.1.2',
        'python-dateutil>=2.8.0',
    ],
    license='MIT',
    url='https://github.com/RegioHelden/django-datawatch',
    download_url='',
    keywords=['django', 'monitoring', 'datawatch', 'check', 'checks'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ]
)
