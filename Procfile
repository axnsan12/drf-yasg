release: python testproj/manage.py migrate
web: gunicorn --chdir testproj testproj.wsgi --log-file -
