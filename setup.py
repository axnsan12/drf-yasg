#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages


def read_req(req_file):
    with open(os.path.join('requirements', req_file)) as req:
        return [line for line in req.readlines() if line and not line.isspace()]


requirements = ['djangorestframework>=3.7.3'] + read_req('base.txt')
requirements_validation = read_req('validation.txt')
requirements_test = read_req('test.txt')

setup(
    name='drf-swagger',
    version='1.0.0rc1',
    packages=find_packages('src', include=['drf_swagger']),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    tests_require=requirements_test,
    extras_require={
        'validation': requirements_validation,
        'test': requirements_test,
    },
    license='BSD License',
    description='Automated generation of real Swagger/OpenAPI 2.0 schemas from Django Rest Framework code.',
    long_description='',
    url='https://github.com/axnsan12/drf-swagger',
    author='Cristi V.',
    author_email='cristi@cvjd.me',
    keywords='drf-swagger drf django rest-framework schema swagger openapi ',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
