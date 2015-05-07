'''
Created on May 2, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

class SimpleAppLoggerConfgigurator(object):
	def __init__(self, appName, logFile = True, logToConsole = True):
		import logging
		self.appName = appName
		appLogger = logging.getLogger('AppLogger')
		self.appLogger = appLogger
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		if (logFile is True):
			logFile = appName + '.log'
		if (logFile is not None):
			logFileHandler = logging.FileHandler(logFile)
			logFileHandler.setFormatter(formatter)
			appLogger.addHandler(logFileHandler)
		if (logToConsole):
			logConsoleHandler = logging.StreamHandler()
			logConsoleHandler.setFormatter(formatter)
			appLogger.addHandler(logConsoleHandler)
		appLogger.setLevel(logging.INFO)
		appLogger.info('==========================================================')
		appLogger.info('Starting ' + appName)
	def __del__(self):
		self.appLogger.info('Finished ' + self.appName)
		self.appLogger.info('==========================================================')