FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN useradd -m user
USER user
