from motor.motor_asyncio import AsyncIOMotorClient
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis
from app.core.config import settings

class Database:
    mongo_client: AsyncIOMotorClient = None
    es_client: AsyncElasticsearch = None

    redis_client: redis.Redis = None

    def connect(self):
        self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.es_client = AsyncElasticsearch(
            hosts=settings.ELASTICSEARCH_URL,
            retry_on_timeout=True
        )
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        print("Connected to MongoDB, Elasticsearch, and Redis")

    async def close(self):
        if self.mongo_client:
            self.mongo_client.close()
        if self.es_client:
            await self.es_client.close()
        if self.redis_client:
            await self.redis_client.close()
        print("Closed database connections")

db = Database()
