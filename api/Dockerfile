FROM python:3.11.8-slim

WORKDIR /app

RUN apt-get update -y
RUN apt-get install -y --no-install-recommends \
build-essential \
libpq-dev

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

ENV MODULE_NAME="src.main"

CMD ["sh", "-c", "make watch prod"]
