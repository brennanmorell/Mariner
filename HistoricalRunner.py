import gdax
import time, calendar
import datetime
import signal, sys

from HistoricalEngine import HistoricalEngine

class HistoricalRunner():
	def __init__(self):
		#BTC_TICKER = 'BTC-USD'
		ETH_TICKER = 'ETH-USD'
		#LTC_TICKER = 'LTC-USD'

		#btc_client = PublicClient(product_id=BTC_TICKER)
		eth_client = gdax.PublicClient()
		#ltc_client = PublicClient(product_id=LTC_TICKER)

		#self.btc_historicalEngine = HistoricalEngine(public_client = btc_client)
		self.eth_historicalEngine = HistoricalEngine(public_client = eth_client, ticker = ETH_TICKER)
		#self.ltc_historicalEngine = HistoricalEngine(public_client = ltc_cliegdax
		self.curr_iso = eth_client.get_time()['iso'] #initialize current time in iso format
		signal.signal(signal.SIGINT, self.signal_handler)

	def signal_handler(self, signal, frame):
		print('Program terminated.')
		self.stop()
		sys.exit(0)


	def start(self):
		print("Starting Runner.")
		self.fetchHistoricalData()
		self.stop()


	def stop(self):
		print("Stopping Runner.")
		#self.btc_historicalEngine.closeWorkbook()
		self.eth_historicalEngine.closeWorkbook()
		#self.ltc_historicalEngine.closeWorkbook()


	def fetchHistoricalData(self):
		times = self.computeTimeIntervals()

		#for time in times:
			#print("time: " + str(time))

		num_requests = len(times)-1

		i = 0
		while i < num_requests:
			if self.eth_historicalEngine.fetchData(times[i], times[i+1]):
				print("")
			else:
				return
			time.sleep(1)
			i+=1
		return


	def computeTimeIntervals(self):
		times = []
		curr_datetime = datetime.datetime.strptime(self.curr_iso, "%Y-%m-%dT%H:%M:%S.%fZ")
		begin_datetime = curr_datetime - datetime.timedelta(days = 10)
		times.append(begin_datetime.isoformat())
		date_time = begin_datetime
		while date_time != curr_datetime:
			times.append(date_time.isoformat())
			date_time+=datetime.timedelta(seconds = 1)
		return times


if __name__ == '__main__':
	runner = HistoricalRunner()
	runner.start()
