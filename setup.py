#!/usr/bin/env python
# -*- coding: utf-8 -*-
import distutils.core
import io
import os
import sys
from setuptools import find_packages, setup

requirements_setup = ['setuptools_scm==1.15.6']


def _install_setup_requires(attrs):
    # copied from setuptools
    dist = distutils.core.Distribution(dict(
        (k, v) for k, v in attrs.items()
        if k in ('dependency_links', 'setup_requires')
    ))
    # Honor setup.cfg's options.
    dist.parse_config_files(ignore_option_errors=True)
    if dist.setup_requires:
        dist.fetch_build_eggs(dist.setup_requires)


if 'sdist' in sys.argv:
    try:
        # try to install setuptools_scm before setuptools does it, otherwise our monkey patch below will come too early
        # (setuptools_scm adds find_files hooks into setuptools on install)
        _install_setup_requires({'setup_requires': requirements_setup})
    except Exception:
        pass

    try:
        # see https://github.com/pypa/setuptools_scm/issues/190, setuptools_scm includes ALL versioned files from
        # the git repo into the sdist by default, and there is no easy way to provide an opt-out;
        # this hack is ugly but does the job; because this is not really a documented interface of the module,
        # the setuptools_scm version should remain pinned to ensure it keeps working
        import setuptools_scm.integration

        setuptools_scm.integration.find_files = lambda _: []
    except ImportError:
        pass


def read_req(req_file):
    with open(os.path.join('requirements', req_file)) as req:
        return [line for line in req.readlines() if line and not line.isspace()]


with io.open('README.rst', encoding='utf-8') as readme:
    description = readme.read()

requirements = ['djangorestframework>=3.7.0'] + read_req('base.txt')
requirements_validation = read_req('validation.txt')

setup(
    name='drf-yasg',
    use_scm_version=True,
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
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Topic :: Documentation',
        'Topic :: Software Development :: Code Generators',
    ],
)
