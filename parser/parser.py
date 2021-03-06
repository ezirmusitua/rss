# -*- coding: utf-8 -*-
import argparse
import hashlib
import datetime
# import uvloop
import asyncio
from feedparser import parse as parse_feed
from motor.motor_asyncio import AsyncIOMotorClient
from html2text import HTML2Text

# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

html2text_handler = HTML2Text()
html2text_handler.ignore_emphasis = True
html2text_handler.ignore_images = True
html2text_handler.ignore_links = True
html2text_handler.ignore_tables = True


class Article(object):
    def __init__(self, parsed_feed):
        self._formatted = Article.extract(parsed_feed)

    @property
    def json(self):
        return self._formatted

    @property
    def exists_query(self):
        return {'hash': self._formatted['hash']}

    @staticmethod
    def extract(content):
        result = dict()
        result['title'] = content['title']
        result['link'] = content['link']
        result['hash'] = hashlib.md5((content['link'] + content['title']).encode()).hexdigest()
        published_at_time_tup = content.get('published_parsed', None)
        if published_at_time_tup:
            result['publish_at'] = datetime.datetime(*content['published_parsed'][:7]).timestamp()
        else:
            result['publish_at'] = -1
        _content, summary = content.get('content', None), content.get('summary', None)

        if not _content and not summary:
            result['description'] = result['content'] = ''
        elif not _content:
            summary_text = html2text_handler.handle(content['summary'])
            result['description'] = summary_text[:200]
            result['content'] = summary_text
            result['content_raw'] = content['summary']
        elif not summary:
            content_text = html2text_handler.handle(content['content'][0]['value'])
            result['description'] = content_text[:200]
            result['content'] = content_text
            result['content_raw'] = content['content'][0]['value']
        else:
            summary_text = html2text_handler.handle(content['summary'])
            content_text = html2text_handler.handle(content['content'][0]['value'])
            result['description'] = summary_text[:200]
            result['content'] = content_text
            result['content_raw'] = content['content'][0]['value']
        result['has_read'] = False
        return result


async def parse(content):
    return parse_feed(content)


async def main(db, interval=60):
    while True:
        sources = await db['feed'].find({}, limit=10).to_list(length=10)
        if not sources:
            print('no feed to parse ... ')
        else:
            done, pending = await asyncio.wait([
                parse(source['content'])
                for source in sources
            ])
            to_save = list()
            for future in done:
                parsed = future.result()
                for content in parsed.get('entries', list()):
                    to_save.append(Article(content))
            print('create new articles')
            await asyncio.wait([
                db['article'].find_one_and_update(article.exists_query, {'$set': article.json}, upsert=True)
                for article in to_save
            ])
            print('removing parsed feeds ... ')
            await db['feed'].remove({'_id': {'$in': list(map(lambda x: x['_id'], sources))}})
        await asyncio.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mongo', metavar='mongo', type=str, nargs='*', help='mongo db uri',
                        default=['mongodb://localhost:27017/rss'])
    args = parser.parse_args()
    mongo_uri = args.mongo[0]
    db = AsyncIOMotorClient(mongo_uri)['rss']
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(db, 3600))
    loop.run_forever()
