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
        bid_whale_order = self.get_bid_whale(price)
        if bid_whale_order is None or volume > bid_whale_order.get_volume():
            #print("    NEW WHALE ENTERED (BID): price=" + str(price) + " volume=" + str(volume))
            bid_whale_order = WhaleOrder(ID, price, volume)
            self.set_bid_whale(price, bid_whale_order)


    def addAskWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        ask_whale_order = self.get_ask_whale(price)
        if ask_whale_order is None or volume > ask_whale_order.get_volume():
            #print("    NEW WHALE ENTERED (ASK): price=" + str(price) + " volume=" + str(volume))
            ask_whale_order = WhaleOrder(ID, price, volume)
            self.set_ask_whale(price, ask_whale_order)


    def removeBidWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        bid_whale_order = self.get_bid_whale(price)
        if bid_whale_order is not None and bid_whale_order.get_id() == ID:
            #print("    WHALE LEFT (BID): price=" + str(price) + " volume=" + str(volume))
            self.remove_bid_whale(price)


    def removeAskWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        ask_whale_order = self.get_ask_whale(price)
        if ask_whale_order is not None and ask_whale_order.get_id() == ID:
            #print("    WHALE LEFT (ASK): price=" + str(price) + " volume=" + str(volume))
            self.remove_ask_whale(price)


    def changeBidWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        new_volume = order['new_size']
        bid_whale_order = self.get_bid_whale(price)
        if not bid_whale_order == None:
            #print("    WHALE CHANGED (BID): price=" + price + " new_volume=" + new_volume)
            if self.isWhale(new_volume):
                bid_whale_order.setVolume(new_volume)
                self.set_bid_whale(price, bid_whale_order)
            else:
                self.removeBidWhale(order)


    def changeAskWhale(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        new_volume = order['new_size']
        ask_whale_order = self.get_ask_whale(price)
        if not ask_whale_order == None:
            #print("    WHALE CHANGED (ASK): price=" + price + " new_volume=" + new_volume)
            if self.isWhale(new_volume):
                ask_whale_order.setVolume(new_volume)
                self.set_ask_whale(price, ask_whale_order)
            else:
                self.removeAskWhale(order)


    def get_top_bid_whale(self):
        if not self._bid_whales.is_empty():
            top_bid = self._bid_whales.max_key()
            return self.get_bid_whale(top_bid)
        else:
            return None


    def get_bid_whale(self, price):
        return self._bid_whales.get(price)


    def remove_bid_whale(self, price):
        self._bid_whales.remove(price)


    def set_bid_whale(self, price, whale):
        self._bid_whales.insert(price, whale)


    def get_top_ask_whale(self):
        if not self._ask_whales.is_empty():
            top_ask = self._ask_whales.min_key()
            return self.get_ask_whale(top_ask)
        else:
            return None


    def get_ask_whale(self, price):
        return self._ask_whales.get(price)


    def remove_ask_whale(self, price):
        self._ask_whales.remove(price)


    def set_ask_whale(self, price, whale):
        self._ask_whales.insert(price, whale)
