import GDAX, time
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
from MarinerOrderBook import MarinerOrderBook

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient

class MarinerStrategy(WebsocketClient):
    def __init__(self, sentiment = 'BULL', ticker = 'BTC-USD', percent = Decimal(.0005)):
        self._sentiment = sentiment
        self._ticker = ticker
        self._percent = Decimal(percent)
        self._public_client = PublicClient(product_id = self._ticker)
        self._threshold = self.computeVolumeThreshold()
        self._book = MarinerOrderBook(ticker = self._ticker, threshold = self._threshold)
        #self._orderBookHandler = MarinerOrderBookHandler()
        self._top_bid_whale = None
        self._top_ask_whale = None


    def computeVolumeThreshold(self):
        stats = self._public_client.getProduct24HrStats(self._ticker)
        volume = Decimal(stats['volume'])
        threshold = self._percent * volume
        return threshold


    def start(self):
        print("    starting whale...")
        self._book.start()
        time.sleep(3) #let data structures warm up
        self._book.registerHandlers(self.bookUpdatedHandler, self.whaleEnteredMarketHandler)


    def bookUpdatedHandler(self):
        return

    def whaleEnteredMarketHandler(self, order):
        print("whale entered market...")
        self.updateTopBidWhale()
        self.updateTopAskWhale()


    def updateTopBidWhale(self):
        bid_whale = self._book.get_top_whale_bid()
        price = bid_whale.get_price()
        volume = bid_whale.get_volume()
        if not bid_whale == None:
            if self._top_bid_whale == None:
                self._top_bid_whale = bid_whale
                print("    top bid whale is now " + str(self._top_bid_whale))
            else:
                if price > self._top_bid_whale.get_price():
                    self._top_bid_whale = bid_whale
                    print("    top bid whale is now " + str(self._top_bid_whale))
                elif price == self._top_bid_whale.get_price() and volume > self._top_bid_whale.get_volume():
                    self._top_bid_whale = bid_whale
                    print("    top bid whale is now " + str(self._top_bid_whale))


    def updateTopAskWhale(self):
        ask_whale = self._book.get_top_whale_ask()
        price = ask_whale.get_price()
        volume = ask_whale.get_volume()
        if not ask_whale == None:
            if self._top_ask_whale == None:
                self._top_ask_whale = ask_whale
                print("    top ask whale is now " + str(self._top_ask_whale))
            else:
                if price > self._top_ask_whale.get_price():
                    self._top_ask_whale = ask_whale
                    print("    top ask whale is now " + str(self._top_ask_whale))
                elif price == self._top_ask_whale.get_price() and volume > self._top_ask_whale.get_volume():
                    self._top_ask_whale = ask_whale
                    print("    top ask whale is now " + str(self._top_ask_whale))

