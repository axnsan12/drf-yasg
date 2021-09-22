.. |br| raw:: html

   <br />

############
Contributing
############

Contributions are always welcome and appreciated! Here are some ways you can contribute.

******
Issues
******

You can and should open an issue for any of the following reasons:

* you found a bug; steps for reproducing, or a pull request with a failing test case will be greatly appreciated
* you wanted to do something but did not find a way to do it after reading the documentation
* you believe the current way of doing something is more complicated or less elegant than it can be
* a related feature that you want is missing from the package

Please always check for existing issues before opening a new issue.

*************
Pull requests
*************

You want to contribute some code? Great! Here are a few steps to get you started:

#. **Fork the repository on GitHub**
#. **Clone your fork and create a branch for the code you want to add**
#. **Create a new virtualenv and install the package in development mode**

   .. code:: console

      $ python -m venv venv
      $ source venv/bin/activate
      (venv) $ python -m pip install -U pip setuptools
      (venv) $ pip install -U -e .[validation]
      (venv) $ pip install -U -r requirements/dev.txt

#. **Make your changes and check them against the test project**

   .. code:: console

      (venv) $ cd testproj
      (venv) $ python manage.py migrate
      (venv) $ python manage.py runserver
      (venv) $ firefox localhost:8000/swagger/

#. **Update the tests if necessary**

   You can find them in the ``tests`` directory.

   If your change modifies the expected schema output, you should regenerate the reference schema at
   ``tests/reference.yaml``:

   .. code:: console

      (venv) $ python testproj/manage.py generate_swagger tests/reference.yaml --overwrite --user admin --url http://test.local:8002/

   After checking the git diff to verify that no unexpected changes appeared, you should commit the new
   ``reference.yaml`` together with your changes.

#. **Run tests. The project is setup to use tox and pytest for testing**

   .. code:: console

      # install test dependencies
      (venv) $ pip install -U -r requirements/test.txt
      # run tests in the current environment, faster than tox
      (venv) $ pytest -n auto --cov
      # (optional) sort imports with isort and check flake8 linting
      (venv) $ isort --apply
      (venv) $ flake8 src/drf_yasg testproj tests setup.py
      # (optional) run tests for other python versions in separate environments
      (venv) $ tox

#. **Update documentation**

   If the change modifies behaviour or adds new features, you should update the documentation and ``README.rst``
   accordingly. Documentation is written in reStructuredText and built using Sphinx. You can find the sources in the
   ``docs`` directory.

   To build and check the docs, run

   .. code:: console

      (venv) $ tox -e docs

#. **Push your branch and submit a pull request to the master branch on GitHub**

   Incomplete/Work In Progress pull requests are encouraged, because they allow you to get feedback and help more
   easily.

#. **Your code must pass all the required CI jobs before it is merged**

   As of now, this consists of running on the supported Python, Django, DRF version matrix (see README),
   and building the docs succesfully.

******************
Maintainer's notes
******************

Release checklist
=================

* update ``docs/changelog.rst`` with changes since the last tagged version
* commit & tag the release - ``git tag x.x.x -m "Release version x.x.x"``
* push using ``git push --follow-tags``
* verify that `Actions`_ has built the tag and successfully published the release to `PyPI`_
* publish release notes `on GitHub`_
* start the `ReadTheDocs build`_ if it has not already started
* deploy the live demo `on Heroku`_


.. _Actions: https://github.com/axnsan12/drf-yasg/actions
.. _PyPI: https://pypi.org/project/drf-yasg/
.. _on GitHub: https://github.com/axnsan12/drf-yasg/releases
.. _ReadTheDocs build: https://readthedocs.org/projects/drf-yasg/builds/
.. _on Heroku: https://dashboard.heroku.com/pipelines/412d1cae-6a95-4f5e-810b-94869133f36a
