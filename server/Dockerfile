#FROM jferroal/alpine-py3.6-be
FROM python:alpine3.6
ENV MONGO_URI mongodb://localhost:27017/rss
RUN pip install -U motor aiohttp graphql-core aiohttp_graphql
WORKDIR /usr/src/spider
ADD . .
CMD python server.py $MONGO_URI
