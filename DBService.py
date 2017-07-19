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
        print(str(tick.iloc[0]))
        #{'trade_id': 7952304, 'price': '217.23000000', 'size': '32.12752755', 'bid': '217.22', 'ask': '217.23', 'volume': '863981.44534800', 'time': '2017-07-19T01:39:36.827000Z'}
        return


    def write_book_state(self, book_state):
        #Logging.logger.info("writing book state to mongo db...")
        #Logging.logger.info(str(book_state))
        return


    def write_whale_state(self, whale_state):
        #Logging.logger.info("writing whale state to mongo db...")
        #Logging.logger.info(str(whale_state))
        return


