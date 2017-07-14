
class WhaleLevel():
	def __init__(self, price, volume, orders, current_whale):
		self._price = price
		self._orders = orders
		self._volume = volume
		self._current_whale = current_whale

	def get_price(self):
		return self._price

	def get_orders(self):
		return self._orders

	def add_order(self, order):
		self._orders.append(order)
		self._volume+=order.get_volume()
		self.update_current_whale()

	def remove_order(self, order):
		self._orders.remove(order)
		self._volume-=order.get_volume()
		self.update_current_whale()

	def get_volume(self):
		return self._volume

	def get_current_whale(self):
		return self._current_whale

	def add_volume(self, volume):
		self._volume+=volume

	def remove_volume(self, volume):
		self._volume-=volume

	def update_current_whale(self):
		max_order = None
		max_volume = 0
		for order in orders:
			if order.get_volume > max_volume:
				max_volume = order.get_volume
				max_order = order
		self.current_whale = max_order


	def __str__(self):
		return "Whale Level [price: " + str(self._price) + " volume: " + str(self._volume) + " current_whale: " + self._current_whale "]"

	def __cmp__(self, other):
		return cmp(self._price, other._price)

