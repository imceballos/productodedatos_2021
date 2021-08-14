FROM python:3.7.3-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ENV TZ=America/Santiago

RUN apt-get update
RUN apt-get install gcc -y

RUN apt-get install default-libmysqlclient-dev -y

RUN pip install --upgrade pip

COPY ./src /usr/src/app

RUN pip install -e .[dev]

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=4", "manage:app"]

ENTRYPOINT [ "./entrypoint.sh" ]