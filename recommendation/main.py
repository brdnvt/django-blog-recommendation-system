import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from moderation import moderate_blog_post
from db import get_recommendations
import aiormq
import asyncio
from auth import get_current_user
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()

    rabbit = f"amqp://{os.environ['AMQP_USER']}:{os.environ['AMQP_PASS']}@{os.environ['AMQP_HOST']}/"

    for i in range(10):
        try:
            connection = await aiormq.connect(rabbit)
            logger.info("Connected to RabbitMQ")
            break
        except (ConnectionRefusedError, aiormq.exceptions.AMQPConnectionError) as e:
            logger.info(f"Failed to connect to RabbitMQ, attempt {i + 1}/10")
            await asyncio.sleep(3)
    else:
        raise Exception("Failed to connect to RabbitMQ")

    channel = await connection.channel()
    await channel.basic_qos(prefetch_count=1)
    
    # Создаем очередь и обмен, если они не существуют
    moderation_queue = os.environ['MODERATION_QUEUE']
    event_exchange = os.environ.get('EVENT_EXCHANGE', 'blog.events')
    routing_key = os.environ.get('ROUTING_KEY_MODERATION', 'blog.event.moderation')
    
    # Создаем обмен
    await channel.exchange_declare(exchange=event_exchange, exchange_type='topic', durable=True)
    
    # Создаем очередь
    await channel.queue_declare(queue=moderation_queue, durable=True)
    
    # Привязываем очередь к обмену
    await channel.queue_bind(queue=moderation_queue, exchange=event_exchange, routing_key=routing_key)
    
    # Подписываемся на очередь
    await channel.basic_consume(moderation_queue, moderate_blog_post)

    yield

    await channel.close()
    await connection.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def api_get_recommendations(user=Depends(get_current_user)):
    # Use user ID from the JWT token
    recommendations = get_recommendations(user)
    return {
        "recommendations": recommendations,
        "user_id": user
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
