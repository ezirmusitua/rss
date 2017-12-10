#FROM jferroal/alpine-py3.6-be
FROM python:alpine3.6
ARG MONGO_URI
RUN pip install -U motor feedparser
WORKDIR /usr/src/parser
ADD . .
CMD python parser.py