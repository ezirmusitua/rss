FROM jferroal/alpine-py3.6-be
RUN pip install -U uvloop motor aiohttp graphql-core aiohttp_graphql
WORKDIR /usr/src/spider
ADD . .
CMD python server.py