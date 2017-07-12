import time
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
from MarinerOrderBook import MarinerOrderBook
from MarinerOrderBookHandler import MarinerOrderBookHandler

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient

class MarinerStrategy(WebsocketClient):
    def __init__(self, sentiment = 'BULL', ticker = 'BTC-USD', threshold = 200):
        self._sentiment = sentiment
        self._publicClient = PublicClient(product_id = ticker)
        self._orderBook = MarinerOrderBook(ticker = ticker, threshold = threshold)
        self._orderBookHandler = MarinerOrderBookHandler()


    def start(self):
        print("    starting whale...")
        self._orderBook.registerHandlers(self._orderBookHandler.topWhaleChangedHandler)
        self._orderBook.start()


    def topWhaleChanged(self):
        print("Best whale changed.")
