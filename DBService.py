import GDAX, time
from decimal import Decimal

class DBService():
    def __init__(self):
        self._connection_string = ""
        self._book_state_table = ""
        self._ticker_table = ""


    def write_ticker(self, tick):
        print("writing ticker to mongo db...")
        print(str(tick))


    def write_book_state(self, book_state):
        print("writing book state to mongo db...")
        print(str(book_state))


