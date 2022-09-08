import json
from kafka import KafkaConsumer

TOPIC_NAME = "twitch_messages"

if __name__ == "__main__":

    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=["kafka:9092"],  # "localhost:9092"
        auto_offset_reset="earliest",
    )

    # Print all messages from the specified Kafka topic.
    for message in consumer:

        print(json.loads(message.value))
