import os
import json
import logging
import pika
from pika.compat import url_unquote
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AMQP_HOST = os.getenv("AMQP_HOST")
RECOMMENDATION_QUEUE = os.getenv("RECOMMENDATION_QUEUE")
EVENT_EXCHANGE = os.getenv("EVENT_EXCHANGE")
ROUTING_KEY_RECOMMENDATION = os.getenv("ROUTING_KEY_RECOMMENDATION")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=AMQP_HOST,
        credentials=pika.credentials.PlainCredentials(
            url_unquote(os.environ["AMQP_USER"]),
            url_unquote(os.environ["AMQP_PASS"])
        )
    )
)
channel = connection.channel()
channel.exchange_declare(exchange=EVENT_EXCHANGE, exchange_type="topic", durable=True)
channel.queue_declare(queue=RECOMMENDATION_QUEUE, durable=True)
channel.queue_bind(queue=RECOMMENDATION_QUEUE, exchange=EVENT_EXCHANGE, routing_key=ROUTING_KEY_RECOMMENDATION)

def process_recommendation(ch, method, properties, body):
    message = json.loads(body.decode())
    logger.info("Received recommendation event: %s", message)
    
    if message["body"]["moderation"]["recommend"]:

        logger.info("Saving blog post %s to recommendations.", message["body"]["post"]["id"])
    else:
        logger.info("Blog post %s not recommended.", message["body"]["post"]["id"])
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=RECOMMENDATION_QUEUE, on_message_callback=process_recommendation)
logger.info("Waiting for recommendation events. To exit press CTRL+C")
channel.start_consuming()
