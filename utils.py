import urllib.parse
import requests
from secret_list import CLIENT_ID, REDIRECT_URI


def build_login_url() -> str:
    """Builds the URL that is used for oAuth."""

    # prepare the payload to login
    data = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID + "@AMER.OAUTHAP",
        "scope": "AccountAccess",
    }

    # url encode the data.
    params = urllib.parse.urlencode(data)

    # build the full URL for the authentication endpoint.
    url = "https://auth.tdameritrade.com/auth?" + params

    return url


def get_access_token(code: str) -> dict:
    """Access token handler for AuthCode Workflow.
    ### Overview:
    ----
    This takes the authorization code parsed from
    the auth endpoint to call the token endpoint
    and obtain an access token.
    ### Returns:
    ----
    {dict} - access token data
    """

    # Define the parameters of our access token post.
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID + "@AMER.OAUTHAP",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "scope": "AccountAccess",
    }

    # Make the request.
    response = requests.post(
        url="https://api.tdameritrade.com/v1/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=data,
    )

    if response.ok:
        return response.json()


def refresh_access_token(refresh_token):

    # build the parameters of our request
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "AccountAccess",
    }

    # Make the request.
    response = requests.post(
        url="https://api.tdameritrade.com/v1/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=data,
    )

    if response.ok:
        return response.json()
