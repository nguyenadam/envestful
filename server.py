from flask import Flask, render_template, redirect, request, session, make_response,session,redirect
import urllib.parse
import requests
app = Flask('app')
app.secret_key = 'dfjasdflhewnfvewnjg2ion2e'

client_id = 'H19TZLKXVJ3GAITABQTFUIBOPNAIMMOC'

def grab_url() -> dict:
    """Builds the URL that is used for oAuth."""

    # prepare the payload to login
    data = {
        'response_type': 'code',
        'redirect_uri': 'https://google.com',
        'client_id': 'H19TZLKXVJ3GAITABQTFUIBOPNAIMMOC' + '@AMER.OAUTHAP'
    }

    # url encode the data.
    params = urllib.parse.urlencode(data)

    # build the full URL for the authentication endpoint.
    url = "https://auth.tdameritrade.com/auth?" + params

    return url

def exchange_code_for_token(code: str, return_refresh_token: bool) -> dict:
    """Access token handler for AuthCode Workflow.
    ### Overview:
    ----
    This takes the authorization code parsed from
    the auth endpoint to call the token endpoint
    and obtain an access token.
    ### Returns:
    ----
    {bool} -- `True` if successful, `False` otherwise.
    """

    # # Parse the URL
    # url_dict = urllib.parse.parse_qs(code)

    # # Grab the Code.
    # url_code = list(url_dict.values())[0][0]
    url_code = code

    # Define the parameters of our access token post.
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id + '@AMER.OAUTHAP',
        'code': url_code,
        'redirect_uri': 'https://google.com'
    }

    if return_refresh_token:
        data['access_type'] = 'offline'

    # Make the request.
    response = requests.post(
        url="https://api.tdameritrade.com/v1/oauth2/token",
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=data
    )
    
    if response.ok:
        return response.json()
        # self._token_save(
        #     token_dict=response.json(),
        #     includes_refresh=True
        # )

        return True

@app.route('/login')
def verify():

    link = grab_url()
    print(link)
    return redirect(link, 302)

@app.route('/api_callback')
def api_callback():
    session.clear()
    code = request.args.get('code')
    token = exchange_code_for_token(code, True)
    print(token)
    # Saving the access token along with all other token related info
    # session["token_info"] = token_info

    return redirect("index")
app.run(host='0.0.0.0', port=8080)