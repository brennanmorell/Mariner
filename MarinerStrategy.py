import GDAX, time
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
from MarinerOrderBook import MarinerOrderBook

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient
from WhaleTracker import WhaleTracker

class MarinerStrategy():
    def __init__(self, sentiment = 'BULL', ticker = 'BTC-USD', percent = Decimal(.0005)):
        self._sentiment = sentiment
        self._public_client = PublicClient(product_id = ticker)
        self._book = MarinerOrderBook(ticker = ticker, threshold = self.computeVolumeThreshold(ticker, Decimal(percent)))
        self._tracker = WhaleTracker(ticker = ticker)
        self._top_bid_whale = None
        self._top_ask_whale = None

    def computeVolumeThreshold(self, ticker, percent):
        stats = self._public_client.getProduct24HrStats(ticker)
        volume = Decimal(stats['volume'])
        threshold = percent * volume
        return threshold


    def start(self):
        print("\nstarting mariner...\n")
        self._book.start()
        time.sleep(3) #let data structures warm up
        self._book.registerHandlers(self.bookUpdatedHandler, self._tracker.whaleEnteredMarketHandler, self._tracker.whaleExitedMarketHandler, self._tracker.whaleChangedHandler)


    def bookUpdatedHandler(self):
        return


