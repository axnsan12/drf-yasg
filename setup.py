#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import io
import os
import sys
from setuptools import find_packages, setup


def read_req(req_file):
    with open(os.path.join('requirements', req_file)) as req:
        return [line.strip() for line in req.readlines() if line.strip() and not line.strip().startswith('#')]


with io.open('README.rst', encoding='utf-8') as readme:
    description = readme.read()

requirements = read_req('base.txt')
requirements_validation = read_req('validation.txt')

py3_supported_range = (5, 7)

# convert inclusive range to exclusive range
py3_supported_range = (py3_supported_range[0], py3_supported_range[1] + 1)
python_requires = ", ".join([">=2.7"] + ["!=3.{}.*".format(v) for v in range(0, py3_supported_range[0])])
python_classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
] + ['Programming Language :: Python :: 3.{}'.format(v) for v in range(*py3_supported_range)]


def drf_yasg_setup(**kwargs):
    setup(
        name='drf-yasg',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        include_package_data=True,
        install_requires=requirements,
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
        python_requires=python_requires,
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Development Status :: 5 - Production/Stable',
            'Operating System :: OS Independent',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Framework :: Django :: 1.11',
            'Framework :: Django :: 2.0',
            'Framework :: Django :: 2.1',
            'Framework :: Django :: 2.2',
            'Topic :: Documentation',
            'Topic :: Software Development :: Code Generators',
        ] + python_classifiers,
        **kwargs
    )


try:
    # noinspection PyUnresolvedReferences
    import setuptools_scm  # noqa: F401

    drf_yasg_setup(use_scm_version=True)
except (ImportError, LookupError) as e:
    if os.getenv('CI', 'false') == 'true' or os.getenv('TRAVIS', 'false') == 'true':
        # don't silently fail on travis - we don't want to accidentally push a dummy version to PyPI
        raise

    err_msg = str(e)
    if 'setuptools-scm' in err_msg or 'setuptools_scm' in err_msg:
        import time
        import traceback

        timestamp_ms = int(time.time() * 1000)
        timestamp_str = hex(timestamp_ms)[2:].zfill(16)
        dummy_version = '1!0.0.0.dev0+noscm.' + timestamp_str

        drf_yasg_setup(version=dummy_version)

        traceback.print_exc(file=sys.stderr)
        print("failed to detect version, package was built with dummy version " + dummy_version, file=sys.stderr)
    else:
        raise
