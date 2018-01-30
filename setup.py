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
    version='0.2.4',
    description='Django Datawatch runs automated data checks in your Django installation',
    author='Jens Nistler <opensource@jensnistler.de>, Bogdan Radko',
    author_email='opensource@regiohelden.de',
    long_description=long_description(),
    install_requires=[
        'celery>=3.1.23',
        'Django>=1.9',
        'django-bootstrap3>=7.0.1',
        'django-extensions>=1.6.7',
        'django-model-utils>=2.5',
        'freezegun>=0.3.7',
        'mock>=2.0.0',
        'python-dateutil>=2.5.3',
    ],
    license='MIT',
    url='https://github.com/RegioHelden/django-datawatch',
    download_url='',
    keywords=['django', 'monitoring', 'datawatch', 'check', 'checks'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ]
)
