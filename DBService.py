import gdax, time
import pymongo as pm
from bson.decimal128 import Decimal128
from decimal import Decimal
from Logging import Logging

class DBService():
    def __init__(self):
        self._connection_string = ""
        self._ticker_table = ""
        self._book_state_table = ""
        self._whale_state_table = ""
        self.db = pm.MongoClient().local


    def write_ticker(self, tick):
        Logging.logger.info("writing ticker to mongo db...")
        tick = self.json_strip_decimal(tick)
        self.db.tick.insert_one(tick)
        return


    def write_book_state(self, book_state):
        Logging.logger.info("writing book state to mongo db...")
        self.db.book.insert_many(book_state.to_dict('records'))
        return


    def write_whale_state(self, whale_state):
        Logging.logger.info("writing whale state to mongo db...")
        elf.db.whale.insert_many(whale_state.to_dict('records'))
        return


    def json_strip_decimal(self, obj):
        for key in obj:
            value = obj[key]
            if type(value) is Decimal:
                obj[key] = Decimal128(val)
        return obj
