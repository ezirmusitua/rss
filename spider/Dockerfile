#FROM jferroal/alpine-py3.6-be
FROM python:alpine3.6
ARG MONGO_URI
RUN pip install -U motor aiohttp
WORKDIR /usr/src/spider
ADD . .
CMD python spider.py