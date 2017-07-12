
class WhaleLevel():
	def __init__(self, price, volume):
		self._price = price
		self._volume = volume

	def get_price(self):
		return self._price

	def set_volume(self, aVolume):
		self._volume = aVolume

	def get_volume(self):
		return self._volume

	def add_volume(self, aVolume):
		self._volume += aVolume

	def remove_volume(self, aVolume):
		self._volume -= aVolume

	def __str__(self):
		return "Whale Level[price: " + str(self._price) + " volume: " + str(self._volume) + "]"

	def __cmp__(self, other):
		return cmp(self._price, other._price)

