# Import the client
from td.client import TDClient

# Create a new session, credentials path is required.
TDSession = TDClient(
    client_id='H19TZLKXVJ3GAITABQTFUIBOPNAIMMOC',
    redirect_uri='https://google.com',
    credentials_path='td_state.json'
)

# Login to the session
TDSession.login()

account = TDSession.get_accounts(fields=["positions"])[1]



def getHoldings(account):
    stocks = account['securitiesAccount']['positions']

    user_stocks = {}

    for stock in stocks:
        name = stock['instrument']['symbol']
        value = stock['marketValue']
        user_stocks[name] = value

    return user_stocks

print(getHoldings(account))