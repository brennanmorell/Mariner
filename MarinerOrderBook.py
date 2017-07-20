import gdax
import time
import collections
import pandas as pd
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal

from WhaleOrder import WhaleOrder
from Logging import Logging

class MarinerOrderBook(gdax.OrderBook):

    current_milli_time = lambda self: int(time.time() * 1000)

    def __init__(self, ticker, threshold):
        gdax.OrderBook.__init__(self, product_id = ticker)
        self._threshold = threshold
        self.bookChanged = None
        self.whaleEnteredMarket = None
        self.whaleExitedMarket = None


    def registerHandlers(self, bookChangedHandler, whaleEnteredMarketHandler, whaleExitedMarketHandler, whaleChangedHandler):
        Logging.logger.info("registering callbacks...")
        self.bookChanged = bookChangedHandler
        self.whaleEnteredMarket = whaleEnteredMarketHandler
        self.whaleExitedMarket = whaleExitedMarketHandler
        self.whaleChanged = whaleChangedHandler


    def onMessage(self, message):
        #Logging.logger.info(message)
        sequence = message['sequence']
        if self._sequence == -1:
            self._asks = RBTree()
            self._bids = RBTree()
            res = self._client.getProductOrderBook(level=3)
            for bid in res['bids']:
                self.add({
                    'id': bid[2],
                    'side': 'buy',
                    'price': Decimal(bid[0]),
                    'size': Decimal(bid[1])
                })
            for ask in res['asks']:
                self.add({
                    'id': ask[2],
                    'side': 'sell',
                    'price': Decimal(ask[0]),
                    'size': Decimal(ask[1])
                })
            self._sequence = res['sequence']

        if sequence <= self._sequence:
            # ignore older messages (e.g. before order book initialization from getProductOrderBook)
            return
        elif sequence > self._sequence + 1:
            Logging.logger.error('Error: messages missing ({} - {}). Re-initializing websocket.'.format(sequence, self._sequence))
            self.close()
            self.start()
            return

        msg_type = message['type']
        if msg_type == 'open':
            self.add(message)
        elif msg_type == 'done' and 'price' in message:
            self.remove(message)
        elif msg_type == 'match':
            self.match(message)
        elif msg_type == 'change':
            self.change(message)

        self._sequence = sequence

        if not self.bookChanged is None:
            self.bookChanged()


    def add(self, order):
        order = {
            'id': order.get('order_id') or order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order.get('size') or order['remaining_size'])
        }

        if order['side'] == 'buy':
            bids = self.get_bids(order['price'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(order['price'], bids)
        else:
            asks = self.get_asks(order['price'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(order['price'], asks)

        if not self.whaleEnteredMarket == None and self.isWhale(order['size']):
            self.whaleEnteredMarket(order)


    def remove(self, order):
        order = {
            'id': order.get('order_id') or order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order.get('size') or order['remaining_size'])
        }
        price = Decimal(order['price'])
        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is not None:
                bids = [o for o in bids if o['id'] != order['id']]
                if len(bids) > 0:
                    self.set_bids(price, bids)
                else:
                    self.remove_bids(price)
        else:
            asks = self.get_asks(price)
            if asks is not None:
                asks = [o for o in asks if o['id'] != order['id']]
                if len(asks) > 0:
                    self.set_asks(price, asks)
                else:
                    self.remove_asks(price)

        if not self.whaleExitedMarket == None and self.isWhale(order['size']):
            self.whaleExitedMarket(order)


    def match(self, order):
        size = Decimal(order['size'])
        price = Decimal(order['price'])

        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if not bids:
                return
            assert bids[0]['id'] == order['maker_order_id']
            if bids[0]['size'] == size:
                self.set_bids(price, bids[1:])
            else:
                bids[0]['size'] -= size
                self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if not asks:
                return
            assert asks[0]['id'] == order['maker_order_id']
            if asks[0]['size'] == size:
                self.set_asks(price, asks[1:])
            else:
                asks[0]['size'] -= size
                self.set_asks(price, asks)


    def change(self, order):
        price = Decimal(order['price'])
        new_volume = Decimal(order['new_size'])
        if order['side'] == 'buy':
            bids = self.get_bids(price)
            if bids is None or not any(o['id'] == order['order_id'] for o in bids):
                return
            index = map(itemgetter('id'), bids).index(order['order_id'])
            bids[index]['size'] = new_size
            self.set_bids(price, bids)
        else:
            asks = self.get_asks(price)
            if asks is None or not any(o['id'] == order['order_id'] for o in asks):
                return
            index = map(itemgetter('id'), asks).index(order['order_id'])
            asks[index]['size'] = new_size
            self.set_asks(price, asks)

        tree = self._asks if order['side'] == 'sell' else self._bids
        node = tree.get(price)

        if node is None or not any(o['id'] == order['order_id'] for o in node):
            return

        if not self.whaleChanged == None and self.isWhale(order['size']):
            self.whaleChanged(order)


    def get_current_book(self, num_levels = 100): #fetch only 1000 levels off book either way
        book = []

        for index, bid_entry in enumerate(self._bids.items([True])):
            if index == num_levels:
                break
            else:
                try:
                    # There can be a race condition here, where a price point is removed
                    # between these two ops
                    thisBid = bid_entry[1]
                except KeyError:
                    continue

                for order in thisBid:
                    book.append(order)

        for index, ask_entry in enumerate(self._asks.items()):
            if index == num_levels:
                break
            else:
                try:
                    # There can be a race condition here, where a price point is removed
                    # between these two ops
                    thisAsk = ask_entry[1]
                except KeyError:
                    continue

                for order in thisAsk:
                    book.append(order)

        book_frame = pd.DataFrame(book)
        return book_frame


    def isWhale(self, aVolume):
        return aVolume >= self._threshold


    #For general book management purposes
    def get_bid(self):
        if not self._bids.is_empty():
            return self._bids.max_key()
        else:
            return None


    def get_bids(self, price):
        return self._bids.get(price)


    def remove_bids(self, price):
        self._bids.remove(price)


    def set_bids(self, price, bids):
        self._bids.insert(price, bids)


    def get_ask(self):
        if not self._asks.is_empty():
            return self._asks.min_key()
        else:
            return None


    def get_asks(self, price):
        return self._asks.get(price)


    def remove_asks(self, price):
        self._asks.remove(price)


    def set_asks(self, price, asks):
        self._asks.insert(price, asks)
