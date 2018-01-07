TESTPROJ="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

PORT=${1:-8002}

set -xe
python "${TESTPROJ}/manage.py" migrate
python "${TESTPROJ}/manage.py" shell -c "import createsuperuser"
python "${TESTPROJ}/manage.py" runserver 0.0.0.0:$PORT
