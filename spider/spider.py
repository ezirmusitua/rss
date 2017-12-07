# -*- coding: utf-8 -*-
import json
import codecs
import uvloop
import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def fetch(session, url):
    async with session.get(url) as response:
        print(url, ':response:', response.status)
        return {'url': url, 'content': await response.text()}


def prepare_urls(path='sites.json'):
    with codecs.open(path, 'rb+', 'utf-8') as rf:
        return json.load(rf)


class CrawlingTask(object):
    def __init__(self, targets=None, interval=60, database=None):
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
                fetch(s, target)
                for target in self.targets
            ])
        self.result = [future.result() for future in done]

    async def do_save(self):
        if not self.result: return
        await self.database['feed'].insert_many(self.result)
        self.result = list()

    def ensure_future(self, loop):
        asyncio.ensure_future(self.crawl(), loop=loop)
        asyncio.ensure_future(self.save())


if __name__ == '__main__':
    urls = prepare_urls()
    db = AsyncIOMotorClient('localhost', 27017)['rss']
    loop = asyncio.get_event_loop()
    t = CrawlingTask(urls, 7200, db)
    t.ensure_future(loop=loop)
    loop.run_forever()
    loop.close()
