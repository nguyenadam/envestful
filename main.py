from flask import Flask, render_template, redirect, request, session, redirect, jsonify
import time
from utils import *
from td.client import TDClient
from secret_list import *
import json

app = Flask("app")
app.secret_key = SECRET_KEY

with open('data.json') as f:
    esg_data = json.load(f)

    esg_data = {k.split('.')[0]: v for k, v in esg_data.items()}


def get_positions(bearer):

    BASE_URL = "https://api.tdameritrade.com/v1/accounts?fields=positions"
    headers = {"Authorization": f"Bearer {bearer}"}

    accounts = requests.get(BASE_URL, headers=headers).json()
    holdings = {}

    for account in accounts:
        if "securitiesAccount" in account:
            for position in account["securitiesAccount"]["positions"]:
                if position["instrument"]["assetType"] == "EQUITY":

                    name = position["instrument"]["symbol"]
                    value = position["marketValue"]

                    if name not in holdings:
                        holdings[name] = value
                    else:
                        holdings[name] += value
    
    return holdings


def get_token(session):
    token_info = session.get("token_info", None)

    # Checking if the session already has a token stored
    if not token_info or "refresh_token" not in token_info:
        return None

    # Refreshing token if it has expired
    if token_info.get("expires_in") < 0:
        token_info = refresh_access_token(token_info.get("refresh_token"))

    session["token_info"] = {**session["token_info"], **token_info}
    return token_info


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


@app.route("/login")
def login():
    return redirect(build_login_url(), 302)


@app.route("/callback")
def api_callback():

    session.clear()
    code = request.args.get("code")
    token_info = get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info

    return redirect("/app")


@app.route("/app")
def go():

    session["token_info"] = get_token(session)
    session.modified = True

    if not session["token_info"]:
        return redirect("/login")

    holdings = get_positions(session["token_info"]["access_token"])

    stock_objs = [{'symbol': stock, 'amount': amount, 'esg': esg_data[stock] if stock in esg_data else None} 
        for stock, amount in holdings.items() if amount > 0]

    return jsonify(stock_objs)


app.run(host="0.0.0.0", port=8080, debug=True)
