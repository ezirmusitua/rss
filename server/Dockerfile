FROM jferroal/alpine-py3.6-be
RUN pip --version
RUN pip install -U uvloop motor feedparser aiohttp graphql-core aiohttp_graphql
WORKDIR /usr/src/spider
ADD . .
CMD ['python', 'server.py', '2>&1', '>', '/dev/null', '&']