import GDAX
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient
from WhaleOrder import WhaleOrder

class MarinerOrderBook(GDAX.OrderBook):
    def __init__(self, ticker, threshold):
        GDAX.OrderBook.__init__(self, product_id = ticker)
        self._threshold = threshold
        self._buyWhales = RBTree()
        self._sellWhales = RBTree()
        self._topBuyWhale = None
        self._topSellWhale = None

    def registerHandlers(self, topWhaleChangedHandler):
        print("    registering callbacks...")
        self.topWhaleChangedHandler = topWhaleChangedHandler

    def onMessage(self, message):
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
            print('Error: messages missing ({} - {}). Re-initializing websocket.'.format(sequence, self._sequence))
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


    def add(self, order):
        order = {
            'id': order.get('order_id') or order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order.get('size') or order['remaining_size'])
        }

        if order['side'] == 'buy':
            self.checkWhaleAddBuy(order)
            bids = self.get_bids(order['price'])
            if bids is None:
                bids = [order]
            else:
                bids.append(order)
            self.set_bids(order['price'], bids)
        else:
            self.checkWhaleAddSell(order)
            asks = self.get_asks(order['price'])
            if asks is None:
                asks = [order]
            else:
                asks.append(order)
            self.set_asks(order['price'], asks)


    def checkWhaleAddBuy(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        if self.isWhale(volume): #too low in practice
            whale_bid_order = self.get_whale_bids(price)
            if whale_bid_order is None or volume > whale_bid_order.get_volume():
                print("WHALE ENTERED (BUY): price=" + str(price) + " volume=" + str(volume))
                whale_bid_order = WhaleOrder(ID, price, volume)
                self.set_whale_bids(price, whale_bid_order)
                top_whale_price = self.get_whale_bid()
                if  self._topBuyWhale is None or top_whale_price != self._topBuyWhale.get_price():
                    self._topBuyWhale = self._buyWhales.get(top_whale_price)
                    self.topWhaleChangedHandler(self._topBuyWhale, "BUY")
                else:
                    print("    top BUY whale is still " + str(self._topBuyWhale))


    def checkWhaleAddSell(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        if self.isWhale(volume): #too low in practice
            whale_ask_order = self.get_whale_asks(price)
            if whale_ask_order is None or volume > whale_ask_order.get_volume():
                print("WHALE ENTERED (SELL): price=" + str(price) + " volume=" + str(volume))
                whale_ask_order = WhaleOrder(ID, price, volume)
                self.set_whale_asks(price, whale_ask_order)
                top_whale_price = self.get_whale_ask()
                if self._topSellWhale is None or top_whale_price != self._topSellWhale.get_price():
                    self._topSellWhale = self._sellWhales.get(top_whale_price)
                    self.topWhaleChangedHandler(self._topSellWhale, "SELL")
                else:
                    print("    top SELL whale is still " + str(self._topSellWhale))


    def remove(self, order):
        order = {
            'id': order.get('order_id') or order['id'],
            'side': order['side'],
            'price': Decimal(order['price']),
            'size': Decimal(order.get('size') or order['remaining_size'])
        }
        price = Decimal(order['price'])
        if order['side'] == 'buy':
            self.checkWhaleRemoveBuy(order)
            bids = self.get_bids(price)
            if bids is not None:
                bids = [o for o in bids if o['id'] != order['id']]
                if len(bids) > 0:
                    self.set_bids(price, bids)
                else:
                    self.remove_bids(price)
        else:
            self.checkWhaleRemoveSell(order)
            asks = self.get_asks(price)
            if asks is not None:
                asks = [o for o in asks if o['id'] != order['id']]
                if len(asks) > 0:
                    self.set_asks(price, asks)
                else:
                    self.remove_asks(price)


    def checkWhaleRemoveBuy(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        whale_bid_order = self.get_whale_bids(price)
        if whale_bid_order is not None and whale_bid_order.get_id() == ID:
            print("WHALE LEFT (BUY): price=" + str(price) + " volume=" + str(volume))
            self.remove_whale_bids(price)
            top_whale_price = self.get_whale_bid()
            if top_whale_price != self._topBuyWhale.get_price():
                self._topBuyWhale = self._buyWhales.get(top_whale_price)
                self.topWhaleChangedHandler(self._topBuyWhale, "BUY")
            else:
                print("    top BUY whale is still " + str(self._topBuyWhale))

    def checkWhaleRemoveSell(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        volume = Decimal(order['size'])
        whale_ask_order = self.get_whale_asks(price)
        if whale_ask_order is not None and whale_ask_order.get_id() == ID:
            print("WHALE LEFT (SELL): price=" + str(price) + " volume=" + str(volume))
            self.remove_whale_asks(price)
            top_whale_price = self.get_whale_ask()
            if top_whale_price != self._topSellWhale.get_price():
                self._topSellWhale = self._sellWhales.get(top_whale_price)
                self.topWhaleChangedHandler(self._topSellWhale, "SELL")
            else:
                print("    top SELL whale is still " + str(self._topSellWhale))


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
            self.checkWhaleChangeBuy(order)
            bids = self.get_bids(price)
            if bids is None or not any(o['id'] == order['order_id'] for o in bids):
                return
            index = map(itemgetter('id'), bids).index(order['order_id'])
            bids[index]['size'] = new_size
            self.set_bids(price, bids)
        else:
            self.checkWhaleChangeSell(order)
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


    def checkWhaleChangeBuy(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        new_volume = order['new_size']
        whale_bid_order = self.get_whale_bids(price)
        if not whale_bid_order == None:
            print("BUY WHALE CHANGED: price=" + price + " new_volume=" + new_volume)
            if self.isWhale(new_volume):
                whale_bid_order.setVolume(new_volume)
                self.set_whale_bids(price, whale_bid_order)
            else:
                self.checkWhaleRemoveBuy(order)


    def checkWhaleChangeBuy(self, order):
        ID = order['id']
        price = Decimal(order['price'])
        new_volume = order['new_size']
        whale_ask_order = self.get_whale_asks(price)
        if not whale_ask_order == None:
            print("SELL WHALE CHANGED: price=" + price + " new_volume=" + new_volume)
            if self.isWhale(new_volume):
                whale_bid_order.setVolume(new_volume)
                self.set_whale_asks(price, whale_ask_order)
            else:
                self.checkWhaleRemoveAsk(order)


    def get_current_book(self):
        result = {
            'sequence': self._sequence,
            'asks': [],
            'bids': [],
        }
        for ask in self._asks:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                thisAsk = self._asks[ask]
            except KeyError:
                continue
            for order in thisAsk:
                result['asks'].append([
                    order['price'],
                    order['size'],
                    order['id'],
                ])
        for bid in self._bids:
            try:
                # There can be a race condition here, where a price point is removed
                # between these two ops
                thisBid = self._bids[bid]
            except KeyError:
                continue

            for order in thisBid:
                result['bids'].append([
                    order['price'],
                    order['size'],
                    order['id'],
                ])
        return result


    def isWhale(self, aVolume):
        return aVolume >= self._threshold

    #For general book management purposes
    def get_ask(self):
        return self._asks.min_key()


    def get_asks(self, price):
        return self._asks.get(price)


    def remove_asks(self, price):
        self._asks.remove(price)


    def set_asks(self, price, asks):
        self._asks.insert(price, asks)


    def get_bid(self):
        return self._bids.max_key()


    def get_bids(self, price):
        return self._bids.get(price)


    def remove_bids(self, price):
        self._bids.remove(price)


    def set_bids(self, price, bids):
        self._bids.insert(price, bids)


    #For whale book management purposes

    def get_whale_ask(self):
        return self._sellWhales.min_key()


    def get_whale_asks(self, price):
        return self._sellWhales.get(price)


    def remove_whale_asks(self, price):
        self._sellWhales.remove(price)


    def set_whale_asks(self, price, asks):
        self._sellWhales.insert(price, asks)


    def get_whale_bid(self):
        return self._buyWhales.max_key()

    def get_whale_bids(self, price):
        return self._buyWhales.get(price)


    def remove_whale_bids(self, price):
        self._buyWhales.remove(price)


    def set_whale_bids(self, price, bids):
        self._buyWhales.insert(price, bids)


"""if __name__ == '__main__':
    import time

    order_book = OrderBook()
    order_book.start()
    time.sleep(10)
    order_book.close()"""