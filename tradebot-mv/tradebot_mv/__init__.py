import Connection
import Fetch

BinanceUs = Connection.Exchange("https://api.binance.us", "BinanceUS")
Fetcher = Fetch.Reader(BinanceUs)
print(Fetcher.getData())
