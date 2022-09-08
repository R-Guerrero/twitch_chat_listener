import requests
import shutil
import subprocess
from time import sleep

BASE_FILE = "dashboard_base.ndjson"
DIRECTORY = "output/"


def get_index_patterns() -> dict:
    """
    This function retrieves all the Kibana index pattern names and ids.
    """

    response = requests.get(
        "http://elasticsearch-kibana:5601/api/saved_objects/_find?fields=title&fields=type&per_page=10000&type=index-pattern",
        headers={"kbn-xsrf": "true"},
        verify=False,
        timeout=30,
    ).json()

    sleep(0.5)

    index_patterns = {}

    for object in response["saved_objects"]:
        if object["type"] == "index-pattern":
            index_patterns[object["attributes"]["title"]] = object["id"]

    return index_patterns


def create_index_pattern(streamer_name: str) -> None:
    """
    This function creates a new Kibana index pattern for the input streamer.
    """

    requests.post(
        "http://elasticsearch-kibana:5601/api/saved_objects/index-pattern",
        json={"attributes": {"title": streamer_name, "timeFieldName": "@timestamp"}},
        headers={"kbn-xsrf": "true"},
        verify=False,
        timeout=30,
    )

    sleep(0.5)


def create_dashboard(streamer_name: str) -> None:
    """
    This function creates a new Kibana dashboard template for the input streamer.
    """

    new_file = f"{streamer_name}_dashboard.ndjson"

    create_index_pattern(streamer_name=streamer_name)

    index_patterns = get_index_patterns()

    shutil.copy(
        src=f"{DIRECTORY}{BASE_FILE}",
        dst=f"{DIRECTORY}{new_file}",
    )

    for i in range(3):  # "new_streamer_name" appears 3 times in the base document.
        subprocess.run(
            [f"sed -i 's/new_streamer_name/{streamer_name}/' {DIRECTORY}{new_file}"],
            shell=True,
        )

        sleep(0.1)

    for i in range(37):  # "new_index_pattern" appears 37 times in the base document.
        subprocess.run(
            [
                f"sed -i 's/new_index_pattern/{index_patterns[streamer_name]}/' {DIRECTORY}{new_file}"
            ],
            shell=True,
        )
