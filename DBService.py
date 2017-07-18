import gdax, time

from decimal import Decimal
from Logging import Logging

class DBService():
    def __init__(self):
        self._connection_string = ""
        self._ticker_table = ""
        self._book_state_table = ""
        self._whale_state_table = ""


    def write_ticker(self, tick):
        #Logging.logger.info("writing ticker to mongo db...")
        print(str(tick))
        return


    def write_book_state(self, book_state):
        #Logging.logger.info("writing book state to mongo db...")
        print(str(book_state))
        return


    def write_whale_state(self, whale_state):
        #Logging.logger.info("writing whale state to mongo db...")
        print(str(whale_state))
        return


