import requests


def validate_token(access_token: str) -> str:
    """
    This function makes an HTTP request to check whether a given Twitch authentication token is valid or not.

    Parameters:
    ---------------
        access_token:
            The authentication token linked to a user (e.g. 43rip6j6fgio8n5xly1oum1lph8ikl1).

    Returns:
    ---------------
        The username linked to the authentication token or, in case the token is not valid, "None".
    """

    headers = {"Authorization": f"OAuth {access_token}"}

    response = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)

    # HTTP response status code 200 shows that a request has been processed correctly.
    if "200" not in str(response):
        return None

    client_id, username, *_ = response.json().values()

    return username
