release: python testproj/manage.py migrate && python testproj/manage.py shell -c "import createsuperuser"
web: gunicorn --chdir testproj testproj.wsgi --log-file -
