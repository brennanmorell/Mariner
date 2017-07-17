import logging

class Logging():
	FORMAT = '[%(levelname)s]: %(asctime)-15s'
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger('Mariner')
	ch = logging.StreamHandler()
	logger.addHandler(ch)
	logger.setLevel(logging.INFO)
		

