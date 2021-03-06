# -*- coding: utf-8 -*-
import argparse
from collections import namedtuple
from aiohttp import web
from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLString,
    GraphQLFloat,
    GraphQLList,
    GraphQLInt
)
from graphql.execution.executors.asyncio import AsyncioExecutor
from aiohttp_graphql import GraphQLView
from motor.motor_asyncio import AsyncIOMotorClient

parser = argparse.ArgumentParser()
parser.add_argument('mongo', metavar='mongo', type=str, nargs='*', help='mongo db uri',
                    default=['mongodb://localhost:27017/rss'])
args = parser.parse_args()
mongo_uri = args.mongo[0]

article_collection = AsyncIOMotorClient(mongo_uri)['rss']['article']

Article = namedtuple('Article', 'title link hash publish_at description content')

ArticleType = GraphQLObjectType(
    name='article',
    description='article from feed',
    fields={
        'title': GraphQLField(
            type=GraphQLString,
            description='article title'
        ),
        'link': GraphQLField(
            type=GraphQLString,
            description='article link'
        ),
        'hash': GraphQLField(
            type=GraphQLString,
            description='article link md5 hash, for duplication check'
        ),
        'publish_at': GraphQLField(
            type=GraphQLFloat,
            description='article publish at'
        ),
        'description': GraphQLField(
            type=GraphQLString,
            description='article description'
        ),
        'content': GraphQLField(
            type=GraphQLString,
            description='article content'
        )
    }
)


async def query_articles_resolver(*_):
    _articles = await article_collection.find({'has_read': False}).to_list(length=None)
    articles = [Article(
        title=article['title'],
        link=article['link'],
        hash=article['hash'],
        publish_at=article['publish_at'],
        description=article['description'],
        content=article['content']
    ) for article in _articles]
    return articles


async def set_articles_read_resolver(*_):
    result = await article_collection.update({}, {'$set': {'has_read': True}}, upsert=False, multi=True)
    return result['nModified']


schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='RootQueryType',
        fields={
            'articles': GraphQLField(
                type=GraphQLList(ArticleType),
                resolver=query_articles_resolver
            )
        }
    ),
    mutation=GraphQLObjectType(
        name='RootMutationType',
        fields={
            'set_articles_read': GraphQLField(
                type=GraphQLInt,
                resolver=set_articles_read_resolver
            )
        }
    )
)


async def enable_cors(_request, response):
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost'
    response.headers['Access-Control-Max-Age'] = '86400'


app = web.Application()

app.on_response_prepare.append(enable_cors)

GraphQLView.attach(
    app,
    schema=schema,
    graphiql=True,
    route_path='/gql',
    executor=AsyncioExecutor(),
    enable_async=True
)

web.run_app(app, port=3081)
