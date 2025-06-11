import json
import logging
import os

import nltk
import pika
import requests
from dotenv import load_dotenv
from nltk.sentiment import SentimentIntensityAnalyzer
from pika.compat import url_unquote

nltk.download("vader_lexicon")

analyzer = SentimentIntensityAnalyzer()
load_dotenv()

AMQP_HOST = os.getenv("AMQP_HOST")
QUEUE = os.getenv("MODERATION_QUEUE")
DLQ_NAME = os.getenv("DLQ_MODERATION")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def text_has_positive_sentiment(text):
    scores = analyzer.polarity_scores(text)
    return scores["pos"] > 0

def moderate_blog_post(ch, method, properties, body):
    try:
        message = json.loads(body.decode())
        blog_post_id = message["body"]["post"]["id"]
        author_id = message["body"]["post"]["author"]["id"]
        author_email = message["body"]["post"]["author"]["email"]
        correlation_id = message["correlationId"]

        response = requests.get(
            os.environ["BLOG_API_URL"] + "/api/posts/" + str(blog_post_id)
        )
        if response.status_code != 200:
            logger.error("Failed to get post information from API: %s (status code: %s)",
                         response.text, response.status_code)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            blog_text = response.json()["text"]
            positive_sentiment = text_has_positive_sentiment(blog_text)
            logger.info("Text has positive statement [bool]: %s", positive_sentiment)
            ch.basic_ack(delivery_tag=method.delivery_tag)

            if positive_sentiment:
                recommendation_event = {
                    'correlationId': correlation_id,
                    'body': {
                        'event': 'BLOG_POST_MODERATED',
                        'post': {
                            'id': blog_post_id,
                            'author': {
                                'id': author_id,
                                'email': author_email
                            }
                        },
                        'moderation': {
                            'sentiment': {
                                'positive': positive_sentiment
                            },
                            'recommend': True
                        }
                    }
                }
                channel = ch  
                channel.basic_publish(
                    exchange=os.environ["EVENT_EXCHANGE"],
                    routing_key=os.environ["ROUTING_KEY_RECOMMENDATION"],
                    body=json.dumps(recommendation_event),
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ),
                )
                logger.info("Recommendation event sent for post %s", blog_post_id)
            else:
                logger.info("Blog post %s not recommended", blog_post_id)
    except Exception as e:
        logger.exception(e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == "__main__":
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.environ["AMQP_HOST"],
            credentials=pika.credentials.PlainCredentials(
                url_unquote(os.environ["AMQP_USER"]),
                url_unquote(os.environ["AMQP_PASS"]),
            ),
        )
    )
    channel = connection.channel()
    channel.basic_consume(queue=QUEUE, on_message_callback=moderate_blog_post)

    print("[*] Waiting for blog post creation events. To exit press CTRL+C")
    channel.start_consuming()
