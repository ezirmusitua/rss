# -*- coding: utf-8 -*-
import asyncio
import aiohttp
# import async_timeout
import uvloop
from motor.motor_asyncio import AsyncIOMotorClient

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def fetch(session, url):
    async with session.get(url) as response:
        print(url, ':response:', response.status)
        text = await response.text()
        return dict(url=url, response_text=text)


class CrawlingTask(object):
    def __init__(self, interval=60, database=None):
        self.urls = [
            'http://liqi.io/feed/',
            'http://cnc.dm5.com/rss-kongbuqishi/',
            'https://sspai.com/feed',
            'https://www.leiphone.com/feed/',
            'http://www.dm5.com/rss-gywzshcwslmnjs/',
            'http://www.dm5.com/rss-jiroushaonv-eling-nengjuduoshaogongjin/',
            'https://sdk.cn/site/rss-content',
            'https://www.appinn.com/feed/',
            'http://feed.iplaysoft.com/',
            'https://imququ.com/feed',
            'http://cizixs.com/feed.xml',
        ]
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
                fetch(s, url)
                for url in self.urls
            ])
        self.result = [future.result() for future in done]

    async def do_save(self):
        if not self.result: return
        await self.database['article'].insert_many(self.result)
        self.result = list()

    def ensure_future(self, loop):
        asyncio.ensure_future(self.crawl(), loop=loop)
        asyncio.ensure_future(self.save())


if __name__ == '__main__':
    urls = list()
    loop = asyncio.get_event_loop()
    db = AsyncIOMotorClient('localhost', 27017)['rss']
    t = CrawlingTask(30, db)
    t.ensure_future(loop=loop)
    loop.run_forever()
    loop.close()
