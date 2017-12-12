.. |br| raw:: html

   <br />

############
Contributing
############

Contributions are always welcome and appreciated! Here are some ways you can contribut.

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

#. Fork the repository on GitHub
#. Clone your fork and create a branch for the code you want to add
#. Create a new virtualenv and install the package in development mode

   .. code:: console

      $ virtualenv venv
      $ source venv/bin/activate
      (venv) $ pip install -e .[validation,test]
      (venv) $ pip install -r requirements/dev.txt

#. Make your changes and check them against the test project

   .. code:: console

      (venv) $ cd testproj
      (venv) $ python manage.py runserver
      (venv) $ curl localhost:8000/swagger.yaml

#. Update the tests if necessary

   You can find them in the ``tests`` directory.

   If your change modifies the expected schema output, you should download the new generated ``swagger.yaml``, diff it
   against the old reference output in ``tests/reference.yaml``, and replace it after checking that no unexpected
   changes appeared.

#. Run tests. The project is setup to use tox and pytest for testing

   .. code:: console

      # run tests in the current environment, faster than tox
      (venv) $ pytest --cov
      # (optional) run tests for other python versions in separate environments
      (venv) $ tox

#. Update documentation

   If the change modifies behaviour or adds new features, you should update the documentation and ``README.rst``
   accordingly. Documentation is written in reStructuredText and built using Sphinx. You can find the sources in the
   ``docs`` directory.

   To build and check the docs, run

   .. code:: console

      (venv) $ tox -e docs

#. Push your branch and submit a pull request to the master branch on GitHub

   Incomplete/Work In Progress pull requrests are encouraged, because they allow you to get feedback and help more
   easily.

#. Your code must pass all the required travis jobs before it is merged. As of now, this includes running on
   Python 2.7, 3.4, 3.5 and 3.6, and building the docs succesfully.
