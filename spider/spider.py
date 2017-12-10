# -*- coding: utf-8 -*-
import json
import codecs
import uvloop
import asyncio
import aiohttp
import async_timeout
from motor.motor_asyncio import AsyncIOMotorClient

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def fetch(loop, session, url):
    try:
        with async_timeout.timeout(5):
            async with session.get(url) as response:
                return {'url': url, 'content': await response.text()}
    except Exception as e:
        loop.call_exception_handler({
            'message': 'Exception happened while fetching {} with timeout {}'.format(url, 10),
            'exception': e
        })
        return {'url': url, 'content': ''}


def prepare_urls(path='sites.json'):
    with codecs.open(path, 'rb+', 'utf-8') as rf:
        return json.load(rf)


class CrawlingTask(object):
    def __init__(self, loop, targets=None, interval=60, database=None):
        self.loop = loop
        self.targets = targets if targets else list()
        self.result = list()
        self.interval = interval
        self.database = database

    async def crawl(self):
        if not self.interval:
            await self.do_crawl()
            await self.save()
            return
        while True:
            await self.do_crawl()
            await asyncio.sleep(self.interval)

    async def save(self):
        # let it sleep for a while to make sure call later than crawler
        await asyncio.sleep(60)
        print('saving ... ')
        if not self.interval:
            await self.do_save()
            return
        while True:
            await self.do_save()
            await asyncio.sleep(self.interval)

    async def do_crawl(self):
        with aiohttp.ClientSession() as s:
            done, pending = await asyncio.wait([
                fetch(self.loop, s, target)
                for target in self.targets
            ])
        self.result = [future.result() for future in done]

    async def do_save(self):
        if not self.result: return
        await self.database['feed'].insert_many(self.result)
        self.result = list()

    def ensure_future(self):
        asyncio.ensure_future(self.crawl(), loop=self.loop)
        asyncio.ensure_future(self.save())


def handle_async_exception(_loop, ctx):
    print('Exception happened: ', ctx)


if __name__ == '__main__':
    urls = prepare_urls()
    db = AsyncIOMotorClient('mongodb://localhost:27017')['rss']
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_async_exception)
    t = CrawlingTask(loop, urls, 7200, db)
    t.ensure_future()
    loop.run_forever()
    loop.close()
