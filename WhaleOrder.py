
class WhaleOrder():
	def __init__(self, ID, price, volume):
		self._id = ID
		self._price = price
		self._volume = volume

	def get_id(self):
		return self._id

	def get_price(self):
		return self._price

	def set_volume(self, aVolume):
		self._volume = aVolume

	def get_volume(self):
		return self._volume

	def __str__(self):
		return "Whale Order [price: " + str(self._price) + " volume: " + str(self._volume) + "]"

	def __cmp__(self, other):
		return cmp(self._price, other._price)

