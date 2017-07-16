import logging

class Logging():
	logger = logging.getLogger()
	ch = logging.StreamHandler()
	logger.addHandler(ch)
	logger.setLevel(logging.INFO)
		

