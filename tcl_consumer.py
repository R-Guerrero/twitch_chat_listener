from concurrent.futures import ThreadPoolExecutor
import json
from kafka import KafkaConsumer
import subprocess
import warnings

from packages.elastic_pkg import kibana
from packages.mongodb_pkg import database

subprocess.run(["clear"])
print("\nImporting the RoBERTa Hugging Face pre-trained Transformers model...\n")
from packages.huggingface_pkg import roberta_pt

warnings.filterwarnings("ignore")
subprocess.run(["clear"])
print("\nRoBERTa Hugging Face pre-trained NLP model is ready.\n")

PROCESSES = 100
TOPIC_NAME = "twitch_messages"

if __name__ == "__main__":

    # This MongoDB client is needed to input new processed
    # documents into the processed messages database.
    mongodb_processed = database.create_mongodb(
        first_client=False, optional_network="mongodb_processed"
    )

    # This Elasticsearch object is needed to push new messages into Elasticsearch.
    elastic_obj = kibana.create_es_obj(host="elasticsearch-kibana", port=9200)

    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=["kafka:9092"],  # "localhost:9092"
        auto_offset_reset="earliest",
    )

    def process_messages(input_str: str) -> None:
        """
        This function serves as pipeline to apply the pretrained Hugging Face transformers
        sentiment classifier model RoBERTa (Robustly Optimized BERT Pretraining Approach)
        and send the processed message to MongoDB and Elasticsearch.
        """

        data = json.loads(input_str.value)

        streamer_name = data["streaming"]
        msg = data["message"]

        # Empty preprocessed messages will be labeled as "neutral".
        if msg:
            (
                data["probability"],
                data["sentiment"],
            ) = roberta_pt.get_sentiment_probability_pt(msg).values()

        else:
            data["probability"], data["sentiment"] = [1, "neutral"]

        # Print processed data.
        print(
            {
                key: value
                for key, value in data.items()
                if key not in ["timestamp", "user"]
            }
        )

        # Send the processed message to the processed MongoDB client/instance.
        database.insert_documents(
            client=mongodb_processed,
            db_name="processed",
            col_name="messages",
            msg=dict(data),
        )

        # Send the processed message to Elasticsearch, omitting the empty ones.
        if msg:
            kibana.push_to_index(
                es_object=elastic_obj, index_name=streamer_name, message=data
            )

    with ThreadPoolExecutor(PROCESSES) as executor:
        executor.map(process_messages, consumer)
