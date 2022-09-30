import requests

resp = requests.get('https://api.binance.us/api/v3/ticker/price?symbol=ETHUSD')

print(resp.json())
