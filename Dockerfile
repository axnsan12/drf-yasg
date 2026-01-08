FROM python:3.11-slim
WORKDIR /build

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libpq-dev
RUN rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src src
RUN pip install .

COPY requirements requirements
RUN pip install -r requirements/testproj.txt
RUN pip install psycopg2-binary gunicorn whitenoise

COPY testproj .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

CMD ["gunicorn", "testproj.wsgi:application", "--bind", "0.0.0.0:80"]
