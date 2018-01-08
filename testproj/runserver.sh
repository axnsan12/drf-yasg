TESTPROJ="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -xe
python "${TESTPROJ}/manage.py" migrate
python "${TESTPROJ}/manage.py" shell -c "import createsuperuser"
gunicorn --chdir "${TESTPROJ}" testproj.wsgi --log-file -
