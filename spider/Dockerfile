FROM jferroal/alpine-py3.6-be
RUN pip install -U uvloop motor feedparser aiohttp
WORKDIR /usr/src/spider
ADD . .
CMD ['python', 'spider.py', '2>&1', '>', '/dev/null', '&']