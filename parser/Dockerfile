FROM jferroal/alpine-py3.6-be
RUN pip install -U uvloop motor feedparser
WORKDIR /usr/src/parser
ADD . .
CMD python parser.py