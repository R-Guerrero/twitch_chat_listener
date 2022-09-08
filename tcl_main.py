from datetime import datetime
import json
import numpy as np
import re
import socket
from threading import Thread
from time import sleep

from packages.elastic_pkg import kibana, dashboard
from packages.kafka_pkg import producer
from packages.logging_pkg import logger
from packages.mongodb_pkg import database
from packages.preprocessing_pkg import preprocessor
from packages.twitch_pkg import emotes, status, tokens
from packages.gui_pkg import menu


# A valid Twitch user authentication token to initilize the program.
TOKEN = "gc80pkzz168g6cvtt6az3r6qjnqcw6"
USERNAME = tokens.validate_token(TOKEN)

if not USERNAME:
    print("Invalid Twitch user token.")
    exit()

raw_logger = logger.setup_logger("raw_logger", "output/raw.txt")
preprocessed_logger = logger.setup_logger("processed_logger", "output/preprocessed.txt")

# This MongoDB client is needed to input new raw documents into the raw messages database.
mongodb_raw = database.create_mongodb(
    first_client=True,
    optional_network="mongodb_raw",
    optional_db_name="raw",
    optional_col_name="messages",
)

# This MongoDB client is needed to access to the processed database from the UI.
mongodb_processed = database.create_mongodb(
    first_client=True,
    optional_network="mongodb_processed",
    optional_db_name="processed",
    optional_col_name="messages",
)

# This Elasticsearch object is needed to create the index for each streaming.
elastic_obj = kibana.create_es_obj(host="elasticsearch-kibana", port=9200)


class ChatListener:
    def __init__(self) -> None:
        """
        A socket object from the socket module of the Python Standard Library
        stablishes a connection between a client and a server on a network.
        """

        # socket.socket default parameters.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.settimeout(60)

    def connect(
        self, server: str, port: int, token: str, username: str, channel: str
    ) -> None:
        """
        This method connects a ChatListener() class object to a streaming server.
        """

        # Connect to the server.
        self.server.connect((server, port))
        sleep(0.5)

        # Perform user authentication.
        self.server.send(f"PASS {token}\n".encode("utf-8"))
        self.server.send(f"NICK {username}\n".encode("utf-8"))

        # Join the channel
        self.server.send(f"JOIN {channel}\n".encode("utf-8"))
        sleep(0.5)

        print(f"\t{channel} chat [ON]")

    def get_response(self) -> str:
        """
        This function retrieves messages from the IRC server and keeps the connection alive.
        """

        try:
            response = self.server.recv(2084).decode("utf-8")

            # Send a PONG packet back, whenever the server send a PING packet to the client.
            # This avoids being disconnected, as the server might consider that the connection is closed.
            if response.startswith("PING"):
                self.server.send("PONG\n".encode("utf-8"))
            elif response:
                return response.strip()

        except ConnectionResetError:
            return "ConnectionResetError"

        except ConnectionAbortedError:
            return "ConnectionAbortedError"

        # TimeoutError has been set to 60 seconds in the ChatListener() class __init__ method.
        except TimeoutError:
            return "TimeoutError"


def execute_bot(streamer_name: str) -> None:
    """
    This function creates a ChatListener() class object, stablishes the
    connection with the streamer IRC and keeps retrieving messages.

    An index is created to store all processed messages in Elasticsearch.

    Parameters:
    ---------------
        streamer_name:
            The streamer whose IRC messages are to be retrieved.
    """

    global stop_threads

    irc = ChatListener()

    irc.connect(
        server="irc.chat.twitch.tv",
        port=6667,
        token=f"oauth:{TOKEN}",
        username=USERNAME,
        channel=f"#{streamer_name}",
    )

    while 1:  # Infinite loop.

        if stop_threads:  # Red flag for gracefully stopping all threads.
            break

        irc_response = irc.get_response()

        if irc_response is None:
            continue

        if irc_response == "TimeoutError":
            print(
                f"\n\t{streamer_name} is inactive.",
                r"#" + f"{streamer_name} chat [OFF]",
            )
            break

        if irc_response in ("ConnectionResetError", "ConnectionAbortedError"):
            print(
                f"\n\t{streamer_name} connection failed.",
                f"\t#{streamer_name} chat [OFF]\n",
            )

            break

        msg_list = [line.strip() for line in irc_response.splitlines() if len(line) > 0]

        for msg in msg_list:

            regex = (
                r":.*\!.*@(.*)\.tmi.twitch.tv PRIVMSG #" + f"{streamer_name} :" + "(.*)"
            )

            messages = re.findall(regex, msg)

            if not messages:
                continue

            for message in messages:

                username, text = message

                timestamp = datetime.now().isoformat(sep=" ", timespec="milliseconds")

                data = {
                    "streaming": streamer_name,
                    "timestamp": str(timestamp),
                    "user": username,
                    "message": text,
                }

                # Save the raw data into a log file.
                raw_logger.info(data)

                # Create a new message/document in the raw MongoDB client/instance.
                database.insert_documents(
                    client=mongodb_raw,
                    db_name="raw",
                    col_name="messages",
                    msg=dict(data),
                )

                # Preprocess the input message.
                data["message"] = preprocessor.BERT_preprocessing(
                    input_str=text,
                    streamer_emotes=streamer_emotes[streamer_name],
                    global_emotes=GLOBAL_EMOTES,
                    labeled_emotes=LABELED_EMOTES,
                )

                # Save the processed data into a log file.
                preprocessed_logger.info(data)

                # Send the preprocessed message to a Kakfa topic.
                producer.produce_message(data)


def initialize_threads(streamers: list) -> list:
    """
    This function serves as pipeline to initilize 1-4 CPU threads, each of one will run a Twitch IRC bot.
    IRC stands for Interactive Realy Chat, which is a text-based chat system for instant messaging.

    Parameters:
    ---------------
        streamers:
            The streamers whose IRC messages are to be retrieved.

    Returns:
    ---------------
        A list containing the threads (IRC bots) that have been initilized.
    """

    threads = []

    for streamer in streamers:
        t = Thread(target=execute_bot, args=[streamer], daemon=True)
        threads.append(t)

    for thread in threads:
        thread.start()

    print("\n\tPress [CTRL+C] to stop.\n\tListening...\n")

    return threads


def retrieve_twitch_emotes() -> list:

    print("\tWeb scrapping Twitch emotes from different sources...")

    chrome_driver = emotes.create_driver()

    driver_emotes = emotes.get_global_emotes(
        pages_number=1, scrolls_number=1, driver=chrome_driver
    )

    chrome_driver.quit()  # Close all browser windows and ends the WebDriver session.

    return driver_emotes


def main():

    global streamer_emotes
    global LABELED_EMOTES
    global GLOBAL_EMOTES
    global stop_threads

    LABELED_EMOTES = emotes.get_labeled_emotes()

    GLOBAL_EMOTES = np.setdiff1d(
        retrieve_twitch_emotes(), list(LABELED_EMOTES.keys())
    ).tolist()

    streamer_emotes = {}
    stop_threads = False

    while 1:  # Infinite loop.

        try:
            menu.print_user_menu()

            user_option = input("\n\tType the desired option and press ENTER: ")

            match user_option:

                case "5":

                    print("\n\tShutting down Twitch Chat Listener...\n")
                    sleep(1)
                    exit()

                case "4" | "3":

                    docs_number = 0

                    while docs_number <= 0:
                        try:
                            docs_number = int(
                                input("\tType a number of messages ENTER: ")
                            )
                            if docs_number <= 0:
                                print("\t\tPlease use positive integers only...")

                        except ValueError:
                            print("\t\tPlease use positive integers only...")

                    if user_option == "4":
                        client_input = mongodb_processed
                        msg_status = "processed"
                    else:
                        client_input = mongodb_raw
                        msg_status = "raw"

                    msg_cursor = database.get_documents(
                        client=client_input,
                        db_name=msg_status,
                        col_name="messages",
                        n_doc=docs_number,
                    )

                    if msg_cursor:
                        print(
                            f"\n\tPrinting last {docs_number} {msg_status} messages:\n"
                        )

                        for i, msg in enumerate(msg_cursor):

                            print(
                                f"Message {i+1}",
                                json.dumps(
                                    msg,
                                    indent=10,
                                ),
                                ("\n"),
                            )

                        sleep(5)
                    else:
                        print("\n\tNo messages available yet.")
                        sleep(1)

                case "2":

                    input_streamers = (
                        input("\tType Twitch streamer names, separated by spaces: ")
                        .lower()
                        .split(sep=" ")
                    )

                    for streamer in input_streamers:
                        if not re.match(r"^[\w]+$", streamer):
                            print(
                                "\n\tStreamer names can only contain letters, numbers and underscores."
                            )

                        elif status.check_status(streamer):
                            print(f"\n\t#{streamer} streaming is [ON]")

                        else:
                            print(f"\n\t#{streamer} streaming is [OFF]")

                    sleep(1)

                case "1":

                    stop_threads = False

                    input_streamers = (
                        input("\tType Twitch streamer names, separated by spaces: ")
                        .lower()
                        .split(sep=" ")
                    )

                    # The all() function returns True if all elements in the given iterable are true.
                    if not all(
                        [
                            re.match(r"^[\w]+$", streamer) is not None
                            for streamer in input_streamers
                        ]
                    ):
                        print(
                            "\n\tStreamer names can only contain letters, numbers and underscores."
                        )

                        sleep(1)
                        continue

                    # A list of the streamers that are currently online.
                    streamers_online = [
                        streamer
                        for streamer in input_streamers
                        if status.check_status(streamer)
                    ]

                    # A list of the streamers that are currently offline.
                    streamers_offline = [
                        streamer
                        for streamer in input_streamers
                        if streamer not in streamers_online
                    ]

                    for streamer_name in streamers_offline:
                        print(f"\n\t#{streamer_name} streaming is [OFF]")
                        sleep(1)

                    if streamers_online:

                        new_streamers = [
                            streamer
                            for streamer in streamers_online
                            if streamer not in streamer_emotes
                        ]

                        if new_streamers:

                            chrome_driver = emotes.create_driver()

                            for streamer in new_streamers:

                                # Create de Kibana dashboard template for each new streamer.
                                dashboard.create_dashboard(streamer_name=streamer)

                                print("\n\tDownloading specific streamers emotes...\t")

                                # Include the emotes linked to each streamer in de EMOTES dictionary.
                                streamer_emotes[streamer] = emotes.get_streamer_emotes(
                                    streamer=streamer, driver=chrome_driver
                                )

                            chrome_driver.quit()

                        for streamer in streamers_online:
                            # Ensure that the index, in case it already exists, is deleted so that
                            # Elastichsearch data is restarted.
                            kibana.delete_index(
                                es_object=elastic_obj, index_name=streamer
                            )

                            # Create the Elasticsearch index for each online streaming.
                            kibana.create_index(
                                es_object=elastic_obj, index_name=streamer
                            )

                        threads = initialize_threads(streamers_online)

                        # Loop to keep track of how many threads are still alive.
                        while threads:
                            sleep(0.1)
                            threads = [t for t in threads if t.is_alive()]

                            # Each thread running an IRC bot finishes its execution
                            # whenever the execute_bot() functions is exited.

                        print("\n\tNo streaming active. Application ended.")

                case _:
                    print("\tPlease, select an existing menu option.")
                    sleep(1)

        except KeyboardInterrupt:
            print("\n\t[CTRL+C] captured.\n")

            stop_threads = True

            # Wait until all threads are gracefully finished.
            while threads:
                sleep(1)
                threads = [t for t in threads if t.is_alive()]

        map(database.close_client, [mongodb_raw, mongodb_processed])


if __name__ == "__main__":

    main()
