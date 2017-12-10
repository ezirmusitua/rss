#FROM jferroal/alpine-py3.6-be
FROM python:alpine3.6
ARG MONGO_URI
RUN pip install -U motor aiohttp graphql-core aiohttp_graphql
WORKDIR /usr/src/spider
ADD . .
CMD python server.py $MONGO_URI