#FROM jferroal/alpine-py3.6-be
FROM python:alpine3.6
ENV MONGO_URI mongodb://localhost:27017/rss
RUN pip install -U motor feedparser
WORKDIR /usr/src/parser
ADD . .
CMD python parser.py $MONGO_URI