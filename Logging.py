import logging

class Logging():
	FORMAT = '[%(levelname)s]: %(asctime)-15s %(message)s'
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger('Mariner')
	logger.setLevel(logging.INFO)
		

