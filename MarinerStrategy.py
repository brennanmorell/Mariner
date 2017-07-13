import GDAX, time
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
from MarinerOrderBook import MarinerOrderBook
from MarinerOrderBookHandler import MarinerOrderBookHandler

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient

class MarinerStrategy(WebsocketClient):
    def __init__(self, sentiment = 'BULL', ticker = 'BTC-USD', percent = Decimal(.0005)):
        self._sentiment = sentiment
        self._ticker = ticker
        self._percent = Decimal(percent)
        self._publicClient = PublicClient(product_id = self._ticker)
        self._threshold = self.computeVolumeThreshold()
        self._orderBook = MarinerOrderBook(ticker = self._ticker, threshold = self._threshold)
        self._orderBookHandler = MarinerOrderBookHandler()


    def computeVolumeThreshold(self):
        stats = self._publicClient.getProduct24HrStats(self._ticker)
        volume = Decimal(stats['volume'])
        threshold = self._percent * volume
        print("threshold is " + str(threshold))
        return threshold


    def start(self):
        print("    starting whale...")
        self._orderBook.registerHandlers(self._orderBookHandler.topWhaleChangedHandler)
        self._orderBook.start()


    def topWhaleChanged(self):
        print("Best whale changed.")
