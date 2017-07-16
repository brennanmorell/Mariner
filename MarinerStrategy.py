import GDAX, time
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
from MarinerOrderBook import MarinerOrderBook

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient
from WhaleTracker import WhaleTracker
from DataFeed import DataFeed
from Logging import Logging

class MarinerStrategy():
    def __init__(self, sentiment = 'BULL', ticker = 'BTC-USD', percent = Decimal(.0005)):
        self._sentiment = sentiment
        self._public_client = PublicClient(product_id = ticker)
        self._book = MarinerOrderBook(ticker = ticker, threshold = self.computeVolumeThreshold(ticker, Decimal(percent)))
        self._whale_tracker = WhaleTracker(ticker = ticker)
        self._tick_feed = DataFeed(self._public_client, self._book, self._whale_tracker)
        self._top_bid_whale = None
        self._top_ask_whale = None

    def computeVolumeThreshold(self, ticker, percent):
        stats = self._public_client.getProduct24HrStats(ticker)
        volume = Decimal(stats['volume'])
        threshold = percent * volume
        print("threshold is " + str(threshold))
        return 10


    def start(self):
        Logging.logger.info("starting mariner...")
        self._book.start()
        time.sleep(3) #let data structures warm up
        self._book.registerHandlers(self.bookUpdatedHandler, self._whale_tracker.whaleEnteredMarketHandler, self._whale_tracker.whaleExitedMarketHandler, self._whale_tracker.whaleChangedHandler)
        self._tick_feed.start()


    def bookUpdatedHandler(self):
        self._top_bid = self._book.get_bid()
        self._top_ask = self._book.get_ask()

        self._top_bid_whale = self._whale_tracker.get_top_bid_whale()
        self._top_ask_whale = self._whale_tracker.get_top_ask_whale()

        #Logging.logger.info("    top bid: " + str(self._top_bid))
        #Logging.logger.info("    top ask: " + str(self._top_ask))
        #Logging.logger.info("    top bid whale: " + str(self._top_bid_whale))
        #Logging.logger.info("    top ask whale " + str(self._top_ask_whale))


