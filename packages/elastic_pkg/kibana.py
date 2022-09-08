from elasticsearch import Elasticsearch
from time import sleep


def create_es_obj(host: str, port: int) -> Elasticsearch:
    """
    This function creates and returns an Elasticsearch instance/object
    connected to the specified host and port.
    """

    es_object = Elasticsearch(f"http://{host}:{port}")

    while not es_object.ping():
        sleep(0.5)

    return es_object


def create_index(es_object: Elasticsearch, index_name: str) -> None:
    """
    This function creates the input non existing index
    in the specified Elasticsearch instance.
    """

    request_body = {"settings": {"number_of_shards": 1, "number_of_replicas": 0}}

    if not es_object.indices.exists(index=index_name):

        es_object.indices.create(index=index_name, body=request_body, ignore=400)


def delete_index(es_object: Elasticsearch, index_name: str) -> None:
    """
    This function deletes the input existing index
    in the specified Elasticsearch instance.
    """

    request_body = {"settings": {"number_of_shards": 1, "number_of_replicas": 0}}

    if es_object.indices.exists(index=index_name):

        es_object.indices.delete(index=index_name)


def push_to_index(es_object: Elasticsearch, index_name: str, message: str) -> None:
    """
    This function sends the input message to the specified
    index in the Elasticsearch instance.
    """

    es_object.index(index=index_name, body=message)
