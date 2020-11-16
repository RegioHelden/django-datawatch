# -*- coding: UTF-8 -*-
import os
import re
from os.path import join, dirname
from setuptools import setup, find_packages


def get_version(*file_paths):
    """Retrieves the version from the given path"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


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
    version=get_version("django_datawatch", "__init__.py"),
    description='Django Datawatch runs automated data checks in your Django installation',
    author='Jens Nistler <opensource@jensnistler.de>, Bogdan Radko <bogdan.radko@regiohelden.de>',
    author_email='opensource@regiohelden.de',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    install_requires=[
        'celery>=4.4.0',
        'Django>=2.2',
        'django-bootstrap3>=14.0.0',
        'django-extensions>=3.0.0',
        'django-model-utils>=4.0.0',
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
