import gdax
import xlsxwriter
import os, re, sys, time, datetime, copy, shutil


class HistoricalEngine():
    def __init__(self, public_client, ticker):
        self._client = public_client
        self._ticker = ticker
        self._workbook = xlsxwriter.Workbook(str(self._ticker) + '-HISTORICAL.xlsx')
        self._worksheet = self._workbook.add_worksheet()
        self._rowCount = 0
        self._lastTick = ""
        self._lastTickTime = 0

    def fetchData(self, begin_time, end_time):
        print("Fetching " + self._ticker + "...")
        print("    from " + begin_time + " to " + end_time + ".")
        try:
            historical_data = self._client.get_product_historic_rates(product_id = self._ticker, start = begin_time, end = end_time, granularity='1')
            if str(historical_data) == "[]":
                print("    tick is empty...")
                historical_data = self._lastTick
            else:
                print("    tick has data...")
                self._lastTick = historical_data
                print("test " + str(historical_data[0]))
                self._lastTickTime = historical_data[0][0]

        except OSError as e:
            print("Caught Error in " + str(self._ticker) + ".")
            print("    closing " + str(self._ticker) + " workbook...")
            self._workbook.close()
            return False

        for stats in historical_data:
            stat_time = self._lastTickTime
            stat_low = stats[1]
            stat_high = stats[2]
            stat_open = stats[3]
            stat_close = stats[4]
            stat_volume = stats[5]
            self.writeXLSX(stat_time, stat_low, stat_high, stat_open, stat_close, stat_volume)

        return True

    def writeXLSX(self, stat_time, stat_low, stat_high, stat_open, stat_close, stat_volume):
        print("    writing " + str(self._ticker) + " workbook...")
        self._worksheet.write(self._rowCount, 0, stat_time)
        self._worksheet.write(self._rowCount, 1, stat_low)
        self._worksheet.write(self._rowCount, 2, stat_high)
        self._worksheet.write(self._rowCount, 3, stat_open)
        self._worksheet.write(self._rowCount, 4, stat_close)
        self._worksheet.write(self._rowCount, 5, stat_volume)
        self._rowCount+=1

    def closeWorkbook(self):
        print("    closing " + str(self._ticker) + " workbook...")
        self._workbook.close()


#if __name__ == '__main__':
    #run if treated as exec
