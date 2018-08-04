#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import random
import string
import sys
from setuptools import find_packages, setup


def read_req(req_file):
    with open(os.path.join('requirements', req_file)) as req:
        return [line.strip() for line in req.readlines() if line.strip() and not line.strip().startswith('#')]


with io.open('README.rst', encoding='utf-8') as readme:
    description = readme.read()

requirements = read_req('base.txt')
requirements_setup = read_req('setup.txt')
requirements_validation = read_req('validation.txt')


try:
    # this is a workaround for being able to install the package from source without working from a git checkout
    # it is needed for building succesfully on Heroku
    from setuptools_scm import get_version
except ImportError:
    get_version = None

try:
    version = get_version()
    version_kwargs = {'use_scm_version': True}
except Exception:
    if any(any(dist in arg for dist in ['sdist', 'bdist']) for arg in sys.argv):
        raise

    import time
    timestamp_ms = int(time.time() * 1000)
    timestamp_str = hex(timestamp_ms)[2:].zfill(16)
    version_kwargs = {'version': '0.0.0.dummy+' + timestamp_str}

setup(
    name='drf-yasg',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    setup_requires=requirements_setup,
    extras_require={
        'validation': requirements_validation,
    },
    license='BSD License',
    description='Automated generation of real Swagger/OpenAPI 2.0 schemas from Django Rest Framework code.',
    long_description=description,
    url='https://github.com/axnsan12/drf-yasg',
    author='Cristi V.',
    author_email='cristi@cvjd.me',
    keywords='drf django django-rest-framework schema swagger openapi codegen swagger-codegen '
             'documentation drf-yasg django-rest-swagger drf-openapi',
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Topic :: Documentation',
        'Topic :: Software Development :: Code Generators',
    ],
    **version_kwargs
)
