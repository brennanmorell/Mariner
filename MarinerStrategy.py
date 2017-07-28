import gdax
import time, threading
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
from MarinerOrderBook import MarinerOrderBook

#from gdax.public_client import PublicClient
#from gdax.websocket_client import WebsocketClient
from WhaleTracker import WhaleTracker
from DataFeed import DataFeed
from Logging import Logging

class MarinerStrategy():
    def __init__(self, sentiment = 'BULL', ticker = 'BTC-USD', percent = Decimal(.0005)):
        self._sentiment = sentiment
        self._ticker = ticker
        self._public_client = gdax.PublicClient()
        self._book = MarinerOrderBook(ticker = self._ticker, threshold = self.computeVolumeThreshold(Decimal(percent)))
        self._whale_tracker = WhaleTracker(ticker = self._ticker)
        self._feed = DataFeed(self._public_client, self._book, self._whale_tracker, self._ticker)
        self._top_bid_whale = None
        self._top_ask_whale = None
        
    def computeVolumeThreshold(self, percent):
        stats = self._public_client.get_product_24hr_stats(self._ticker)
        volume = Decimal(stats['volume'])
        threshold = percent * volume
        return 10


    def run(self):
        Logging.logger.info("starting mariner...")
        self._book.start() #thread 1 (start is by default on a separate thread)
        time.sleep(3) #let data structures warm up
        self._book.registerHandlers(self.bookUpdatedHandler, self._whale_tracker.whaleEnteredMarketHandler, self._whale_tracker.whaleExitedMarketHandler, self._whale_tracker.whaleChangedHandler)
        t2 = threading.Thread(name = 'data_feed', target = self._feed.start())
        t2.start()


    def bookUpdatedHandler(self):
        self._top_bid = self._book.get_bid()
        self._top_ask = self._book.get_ask()

        self._top_bid_whale = self._whale_tracker.get_top_bid_whale()
        self._top_ask_whale = self._whale_tracker.get_top_ask_whale()

        self.adjustOrders()
        #Logging.logger.info("    top bid: " + str(self._top_bid))
        #Logging.logger.info("    top ask: " + str(self._top_ask))
        #Logging.logger.info("    top bid whale: " + str(self._top_bid_whale))
        #Logging.logger.info("    top ask whale " + str(self._top_ask_whale))

