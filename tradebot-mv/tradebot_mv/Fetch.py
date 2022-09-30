import requests


class Reader:

  def __init__(self, Exchange):
    self.Exchange = Exchange

  def getData(self):
    resp = requests.get(
      'https://api.binance.us/api/v3/ticker/price?symbol=ETHUSD')
    return resp
