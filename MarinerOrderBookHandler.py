import time
from operator import itemgetter
from bintrees import RBTree
from decimal import Decimal
from MarinerOrderBook import MarinerOrderBook

from GDAX.PublicClient import PublicClient
from GDAX.WebsocketClient import WebsocketClient

class MarinerOrderBookHandler(WebsocketClient):
    def __init__(self):
        print("    initializing whale order book handler...")


    def topWhaleChangedHandler(self, top_whale_level, side):
        print("    top " + side + " whale level is now " + str(top_whale_level))
