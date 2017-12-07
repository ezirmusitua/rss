# -*- coding: utf-8 -*-
import hashlib
import datetime
import uvloop
import asyncio
from feedparser import parse as parse_feed
from motor.motor_asyncio import AsyncIOMotorClient

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


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
        result['publish_at'] = datetime.datetime(*content['published_parsed'][:7]).timestamp()
        _content, summary = content.get('content', None), content.get('summary', None)

        if not _content and not summary:
            result['description'] = result['content'] = ''
        elif not _content:
            result['description'] = content['summary'][:500]
            result['content'] = content['summary']
        elif not summary:
            result['description'] = content['content'][0]['value'][:500]
            result['content'] = content['content'][0]['value']
        else:
            result['description'] = content['summary']
            result['content'] = content['content'][0]['value']
        result['has_read'] = False
        return result


async def parse(content):
    return parse_feed(content)


async def main(db, interval=60):
    while True:
        sources = await db['feed'].find({}, limit=10).to_list(length=10)
        done, pending = await asyncio.wait([
            parse(source['content'])
            for source in sources
        ])
        to_save = list()
        for future in done:
            parsed = future.result()
            for content in parsed.get('entries', list()):
                to_save.append(Article(content))
        await asyncio.wait([
            db['article'].find_one_and_update(article.exists_query, {'$set': article.json}, upsert=True)
            for article in to_save
        ])
        await db['feed'].remove({'_id': {'$in': list(map(lambda x: x['_id'], sources))}})
        await asyncio.sleep(interval)


if __name__ == '__main__':
    db = AsyncIOMotorClient('localhost', 27017)['rss']
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(db, 7200))
    loop.run_forever()
