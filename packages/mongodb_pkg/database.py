from pymongo import MongoClient

USER = "root"
PASSWORD = "rootpassword"


def create_mongodb(
    first_client: bool,
    optional_network: str = None,
    optional_db_name: str = None,
    optional_col_name: str = None,
) -> MongoClient:
    """
    This function creates a MongoDB client.

    Parameters:
    ---------------
        first_client:
            Parameter to determine if the client will be
            the first one connected to the network.

        optional_network:
            Optional parameter to specify the network to connect.

        optional_db_name:
            Optional parameter to specify the database to be created

        optional_col_name:
            Optional parameter to specify the collection to be created.

    Returns:
    ---------------
        A MongoDB client with the desired network, database and collection.
    """

    if not optional_network:
        optional_network = "localhost"

    mongo_client = MongoClient(f"mongodb://{USER}:{PASSWORD}@{optional_network}:27017/")

    if first_client:
        for db in mongo_client.list_database_names():
            if db not in ["admin", "config", "local"]:
                mongo_client.drop_database(db)

    # Create the database.
    if optional_db_name:
        create_database(client=mongo_client, db_name=optional_db_name)

    # Create the collection.
    if optional_col_name:
        create_collection(
            client=mongo_client, db_name=optional_db_name, col_name=optional_col_name
        )

    return mongo_client


def create_database(client: MongoClient, db_name: str) -> None:
    """
    This function creates a database in the input MongoDB client.
    """

    db = client[db_name]


def create_collection(client: MongoClient, db_name: str, col_name: str) -> None:
    """
    This function creates a collection in the specified
    database of the input MongoDB client.
    """

    client[db_name].create_collection(name=col_name)


def get_collection_names(client: MongoClient, db_name: str) -> list:
    """
    This function returns all the collections from the specified database.
    """

    return list(client[db_name].list_collection_names())


def insert_documents(
    client: MongoClient, db_name: str, col_name: str, msg: dict
) -> None:
    """
    This function inserts a message/document in the specified collection.
    """

    client[db_name][col_name].insert_one(msg)


def get_documents(client: MongoClient, db_name: str, col_name: str, n_doc: int) -> list:
    """
    This function returns all the messages/documents
    from the specified collection.
    """

    msg_cursor = list(client[db_name][col_name].find())  # .skip(2).limit(3)

    # Transform the field "_id" (instance of ObjectId) into a string.
    if msg_cursor:
        for msg in msg_cursor:
            msg["_id"] = str(msg["_id"])

    return list(reversed(msg_cursor[-n_doc:]))


def drop_collection(client: MongoClient, db_name: str, col_name: str) -> None:
    """
    This function deletes a collection from the specified database.
    """

    client[db_name][col_name].drop()


def close_client(client: MongoClient) -> None:
    """
    This function disconnects the specified MongoDB client.
    If this client/instance is used again it will be automatically re-opened.
    """

    client.close()
