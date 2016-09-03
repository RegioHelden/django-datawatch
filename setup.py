# -*- coding: UTF-8 -*-
from setuptools import setup


setup(
    name='django-monitoring',
    packages=['django_monitoring'],
    version='0.1.0',
    description='Django monitoring runs automated data checks in your Django installation',
    author='Jens Nistler',
    author_email='opensource@jensnistler.de',
    install_requires=[
        'celery>=3.1.23',
        'Django>=1.9',
        'django-braces>=1.9.0',
        'django-extensions>=1.6.7',
        'django-model-utils>=2.5',
        'python-dateutil>=2.5.3',
    ],
    license='MIT',
    url='https://github.com/RegioHelden/django-monitoring',
    download_url='',
    keywords=['django', 'monitoring', 'check', 'checks'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
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
