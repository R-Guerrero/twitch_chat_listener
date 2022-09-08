import requests


def check_status(streamer: str) -> bool:
    """
    This function makes an HTTP request to check whether a given Twitch streaming is live or not.

    Parameters:
    ---------------
        streamer:
            The streamer whose streaming is to be checked.

    Returns:
    ---------------
        "True" if the streaming is live; "False" if the streaming is not live.
    """

    contents = requests.get("https://www.twitch.tv/" + streamer).content.decode("utf-8")

    return "isLiveBroadcast" in contents
