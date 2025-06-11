import os
import json
import pika
from pika.compat import url_unquote
from dotenv import load_dotenv
import pymongo
import logging

load_dotenv()
print("Значення RECOMMENDATION_QUEUE:", os.getenv("RECOMMENDATION_QUEUE")) 
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

mongo_server = os.environ['EVENT_STORE_DB_URL']
mongo_client = pymongo.MongoClient(
    f"mongodb://{mongo_server}/",
    username=os.environ['MONGO_USER'],
    password=os.environ['MONGO_PASS']
)
events_db = mongo_client[os.environ['EVENT_STORE_DB']]

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.environ['AMQP_HOST'],
        credentials=pika.credentials.PlainCredentials(
            url_unquote(os.environ['AMQP_USER']),
            url_unquote(os.environ['AMQP_PASS'])
        )
    )
)
channel = connection.channel()

EXCHANGE = os.environ['EVENT_EXCHANGE']
DLQ_EXCHANGE = os.environ['DLQ_EVENT_EXCHANGE']
STORE_QUEUE = os.environ['STORE_QUEUE']
MODERATION_QUEUE = os.environ['MODERATION_QUEUE']
RECOMMENDATION_QUEUE = os.environ['RECOMMENDATION_QUEUE'] 

channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
channel.exchange_declare(exchange=DLQ_EXCHANGE, exchange_type="direct", durable=True)

channel.queue_declare(queue=STORE_QUEUE, durable=True)
channel.queue_declare(queue=os.environ['DLQ_MODERATION'], durable=True)
channel.queue_declare(
    queue=MODERATION_QUEUE,
    durable=True,
    arguments={
        'x-dead-letter-exchange': DLQ_EXCHANGE,
        "x-dead-letter-routing-key": os.environ['DLQ_MODERATION'],
    }
)
channel.queue_declare(queue=RECOMMENDATION_QUEUE, durable=True)

channel.queue_bind(
    queue=STORE_QUEUE,
    exchange=EXCHANGE,
    routing_key="blog.event.#"
)
channel.queue_bind(
    queue=MODERATION_QUEUE,
    exchange=EXCHANGE,
    routing_key=os.environ['ROUTING_KEY_MODERATION']
)
channel.queue_bind(
    queue=RECOMMENDATION_QUEUE,
    exchange=EXCHANGE,
    routing_key=os.environ['ROUTING_KEY_RECOMMENDATION']
)
channel.queue_bind(queue=os.environ['DLQ_MODERATION'], exchange=DLQ_EXCHANGE)

def event_store(ch, method, properties, body):
    message = json.loads(body.decode())
    logger.info("[x] Event is received by event store")
    col = events_db['events']
    col.insert_one(message)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    for x in col.find():
        logger.info(x)

if __name__ == "__main__":
    channel.basic_consume(queue=STORE_QUEUE, on_message_callback=event_store)
    logger.info('[*] Waiting for STORE events. To exit press CTRL+C')
    channel.start_consuming()
