#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        packages=find_packages('src'),
        package_dir={'': 'src'},
        include_package_data=True,
        install_requires=[
            "packaging>=18.0",
            "coreapi>=2.3.3",
            "coreschema>=0.0.4",
            "django>=1.1.0",
            "djangorestframework>=3.8.0",
            "inflection>=0.3.1",
            "ruamel.yaml>=0.16.12",
            "six>=1.15.0",
            "uritemplate>=3.0.1",
        ],
        extras_require={
            "validation": ["swagger-spec-validator>=2.1.0"],
            "lint": ["flake8>=3.5.0"],
            "format": ["autoflake>=1.4.0", "black>=20.8.0", "isort>=4.2.0"],
            "docs": [
                "djangorestframework_camel_case>=0.2.0",
                "Pillow>=4.3.0",
                "readme_renderer[md]>=24.0",
                "sphinx_rtd_theme>=0.2.4",
                "Sphinx>=1.7.0",
                "twine>=1.12.1",
            ],
            "tests": [
                "dj-database-url>=0.4.2",
                "django-cors-headers>=3.0.2",
                "django-filter>=1.1.0",
                "django-oauth-toolkit>=1.3.2",
                "djangorestframework-camel-case>=1.0.3",
                "djangorestframework-recursive>=0.1.2",
                "Pillow>=4.3.0",
                "pytest>=4.6.11",
                "pytest-django>=3.10.0",
                "tox>=3.3.0",
                "user_agents>=1.1.0",
            ],
            "heroku": ["dj-database-url>=0.4.2", "gunicorn>=19.7.1", "psycopg2>=2.7.3", "whitenoise>=3.3.1",],
        },
    )
