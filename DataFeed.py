import GDAX, time
from bintrees import RBTree
from decimal import Decimal

from GDAX.PublicClient import PublicClient
from DBService import DBService
from Logging import Logging

class DataFeed():
    def __init__(self, public_client, book, whale_tracker):
        self._public_client = public_client
        self._book = book
        self._whale_tracker = whale_tracker
        self._db_service = DBService()


    def start(self):
        print("starting...")
        self._open = True
        while self._open:
            self.fetchTicker()
            self.fetchBookState()
            self.fetchWhaleState()


    def stop(self):
        self._open = False


    def fetchTicker(self):
        #Logging.logger.info("fetching ticker...")
        tick = self._public_client.getProductTicker()
        self._db_service.write_ticker(tick)

    def fetchBookState(self):
        #Logging.logger.info("fetching book state...")
        book_state = self._book.get_current_book()
        self._db_service.write_book_state(book_state)


    def fetchWhaleState(self):
        Logging.logger.info("fetching whale state...")
        whale_state = self._whale_tracker.get_current_whales()
        self._db_service.write_whale_state(whale_state)



