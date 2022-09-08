import json
from kafka import KafkaProducer

TOPIC = "twitch_messages"


def serializer(msg: dict) -> json:
    """
    This function serializes the input message as JSON.
    """

    return json.dumps(msg).encode("utf-8")


producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"], value_serializer=serializer  # "localhost:9092"
)


def produce_message(msg: dict) -> None:
    """
    This function sends the input message to the specified Kafka topic.
    """

    producer.send(topic=TOPIC, value=msg)
