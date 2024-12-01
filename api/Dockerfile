FROM python:3.11.8-slim

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt
RUN apt-get update & apt-get install libpq-dev python3-dev

COPY . /app

EXPOSE 8000

ENV MODULE_NAME="src.main"

CMD ["sh", "-c", "uvicorn $MODULE_NAME:app --host 0.0.0.0"]
