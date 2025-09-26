FROM python:3.11-slim
WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libpq-dev
RUN rm -rf /var/lib/apt/lists/*

COPY requirements requirements
RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt
RUN pip install -r requirements/testproj.txt
RUN pip install drf-yasg psycopg2-binary gunicorn whitenoise

COPY testproj .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

CMD ["gunicorn", "testproj.wsgi:application", "--bind", "0.0.0.0:80"]
