import GDAX, time
from bintrees import RBTree
from decimal import Decimal

from GDAX.PublicClient import PublicClient
from DBService import DBService

class DataFeed():
    def __init__(self, public_client, book):
        self._public_client = public_client
        self._book = book
        self._db_service = DBService()


    def start(self):
        print("starting...")
        self._open = True
        while self._open:
            self.fetchTicker()
            self.fetchBookState()


    def stop(self):
        self._open = False


    def fetchTicker(self):
        print("fetching ticker...")
        tick = self._public_client.getProductTicker()
        self._db_service.write_ticker(tick)

    def fetchBookState(self):
        print("fetching book...")
        book_state = self._book.get_current_book()
        print("book " + str(book_state))
        self._db_service.write_book_state(book_state)



