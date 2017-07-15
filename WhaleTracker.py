import GDAX, time
from bintrees import RBTree
from decimal import Decimal

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient
from WhaleOrder import WhaleOrder

class WhaleTracker():
    def __init__(self, ticker):
        self._ticker = ticker
        self._bid_whales = RBTree()
        self._ask_whales = RBTree()


    def whaleEnteredMarketHandler(self, order):
        if order['side'] == 'buy':
            self.addBidWhale(order)
        else:
            self.addAskWhale(order)


    def whaleExitedMarketHandler(self, order):
        if order['side'] == 'buy':
            self.removeBidWhale(order)
        else:
            self.removeAskWhale(order)

    def whaleChangedHandler(self, order):
        if order['side'] == 'buy':
            self.changeBidWhale(order)
        else:
            self.changeAskWhale(order)


    def addBidWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        whale_bid_order = self.get_whale_bid(price)
        if whale_bid_order is None or volume > whale_bid_order.get_volume():
            print("    NEW WHALE ENTERED (BID): price=" + str(price) + " volume=" + str(volume))
            whale_bid_order = WhaleOrder(ID, price, volume)
            self.set_whale_bid(price, whale_bid_order)


    def addAskWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        whale_ask_order = self.get_whale_ask(price)
        if whale_ask_order is None or volume > whale_ask_order.get_volume():
            print("    NEW WHALE ENTERED (ASK): price=" + str(price) + " volume=" + str(volume))
            whale_ask_order = WhaleOrder(ID, price, volume)
            self.set_whale_ask(price, whale_ask_order)


    def removeBidWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        whale_bid_order = self.get_whale_bid(price)
        if whale_bid_order is not None and whale_bid_order.get_id() == ID:
            print("    WHALE LEFT (BID): price=" + str(price) + " volume=" + str(volume))
            self.remove_whale_bid(price)


    def removeAskWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        whale_ask_order = self.get_whale_ask(price)
        if whale_ask_order is not None and whale_ask_order.get_id() == ID:
            print("    WHALE LEFT (ASK): price=" + str(price) + " volume=" + str(volume))
            self.remove_whale_ask(price)


    def changeBidWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        new_volume = order['new_size']
        whale_bid_order = self.get_whale_bid(price)
        if not whale_bid_order == None:
            print("    WHALE CHANGED (BID): price=" + price + " new_volume=" + new_volume)
            if self.isWhale(new_volume):
                whale_bid_order.setVolume(new_volume)
                self.set_whale_bid(price, whale_bid_order)
            else:
                self.removeBidWhale(order)


    def changeAskWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        new_volume = order['new_size']
        whale_ask_order = self.get_whale_ask(price)
        if not whale_ask_order == None:
            print("    WHALE CHANGED (ASK): price=" + price + " new_volume=" + new_volume)
            if self.isWhale(new_volume):
                whale_bid_order.setVolume(new_volume)
                self.set_whale_ask(price, whale_ask_order)
            else:
                self.removeAskWhale(order)


    """def updateTopBidWhale(self):
        bid_whale = self.get_top_whale_bid()
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
        ask_whale = self.get_top_whale_ask()
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
                    print("    top ask whale is now " + str(self._top_ask_whale))"""


    def get_top_whale_bid(self):
        top_bid = self._bid_whales.max_key()
        return self.get_whale_bid(top_bid)


    def get_whale_bid(self, price):
        return self._bid_whales.get(price)


    def remove_whale_bid(self, price):
        self._bid_whales.remove(price)


    def set_whale_bid(self, price, whale):
        self._bid_whales.insert(price, whale)


    def get_top_whale_ask(self):
        top_ask = self._ask_whales.min_key()
        return self.get_whale_ask(top_ask)


    def get_whale_ask(self, price):
        return self._ask_whales.get(price)


    def remove_whale_ask(self, price):
        self._ask_whales.remove(price)


    def set_whale_ask(self, price, whale):
        self._ask_whales.insert(price, whale)

