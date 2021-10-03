from flask import Flask, render_template, redirect, request, session, redirect, jsonify
from datetime import date, datetime, timezone
from utils import *
from td.client import TDClient
from secret_list import *
import json
from suggestions import suggestions

app = Flask(__name__)
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
    if not token_info:
        return None
    
    now = datetime.now(timezone.utc)

    # Refreshing token if it has expired
    if 'refresh_time' not in session or (now - session['refresh_time']).total_seconds() > token_info.get("expires_in"):
        # token_info = refresh_access_token(token_info.get("refresh_token"))
        return None

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
    session['refresh_time'] = datetime.now(timezone.utc)

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

    valid_stocks = [stock for stock in stock_objs if stock['esg']]
    valid_cash = sum([stock['amount'] for stock in valid_stocks])

    total_scores_cash = [ x['esg']['esgScore']['TR.TRESG']['score'] *( x['amount'] / valid_cash) for x in valid_stocks]
    score = sum(total_scores_cash)

    return render_template('data.html', data = json.dumps(stock_objs), stock_data = stock_objs, user_score = score)

@app.route("/build")
def build():
    return render_template('portfolio.html', choices=suggestions)

@app.route("/custom")
def custom():
    holdings = {k.split(".")[0]: float(v) for k, v in request.args.items() if v and v != ""}

    stock_objs = [{'symbol': stock, 'amount': amount, 'esg': esg_data[stock] if stock in esg_data else None} 
        for stock, amount in holdings.items() if amount > 0]

    valid_stocks = [stock for stock in stock_objs if stock['esg']]
    valid_cash = sum([stock['amount'] for stock in valid_stocks])

    total_scores_cash = [ x['esg']['esgScore']['TR.TRESG']['score'] *( x['amount'] / valid_cash) for x in valid_stocks]
    score = sum(total_scores_cash)

    return render_template('data.html', data = json.dumps(stock_objs), stock_data = stock_objs, user_score = score)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
