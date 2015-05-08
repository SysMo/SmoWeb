import numpy as np
import struct
from smo.util.log import SimpleAppLoggerConfgigurator
import mmap
import logging

appLogger = logging.getLogger('AppLogger')

class ChannelInfo(object):
	def __init__(self, name, group, number, unit, start, length):
		self.name = name
		self.group = group
		self.number = number
		self.unit = unit
		self.start = start
		self.length = length
		self.end = self.start + 16 * self.length
	
	def __str__(self):
		return "{}(group = {}, # = {}, unit = {}, start = {}, end = {}, length = {})".format(self.name, self.group, self.number, self.unit, self.start, self.end, self.length)

class AMRFileReader(object):
	def openFile(self, filePath, offset = 0):
		self.filePath = filePath
		f = open(filePath, 'rb')
		appLogger.info('AMRFileReader: Opened file "{}" for reading'.format(filePath))
		self.fh = mmap.mmap(f.fileno(), 0, access = mmap.ACCESS_READ)
		self.fh.seek(offset, 0)
	
	def __del__(self):
		self.fh.close()
	
	def checkEOF(self):
		isEOF = False
		lookAhead = self.fh.read(30)
		if (len(lookAhead) < 30):
			isEOF = True
		elif (lookAhead[:4] in ('\x00\x00\x00\xff', '\x00\x00\x00\x0f')):
			isEOF = True
		elif (lookAhead == 30*'\x00'):
			isEOF = True
		if (not isEOF):
			self.fh.seek(-30, 1)
		return isEOF
	
	def readUntilDelimiter(self, delim):
		result = ''
		while True:
			c = self.fh.read(1)
			result += c
			if (c == delim):
				break
		return result

	def readString(self):
		l, = struct.unpack('B', self.fh.read(1))
		s, = struct.unpack('{}s'.format(l), self.fh.read(l))
		return s
	
	def toHexString(self, s):
		return ":".join("{:02x}".format(ord(c)) for c in s)
	
	def readHeader(self):
		self.fh.seek(0)
		blah = self.readString()
		appLogger.debug(blah)
		pos = self.fh.find('\x00\x04\x01\xFF')
		self.fh.seek(pos + 4)
		appLogger.debug('Header end position: {}'.format(self.fh.tell()))
	
	def getChannelInfo(self):
		# This is something like
		# 00:00:19:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:01:00:03:00:80:80:80:00:02:00:00:00
		# byte 0 is the channel group
		# byte 2 is the channel number
		channelHeader = self.fh.read(30)
		chanGroup = ord(channelHeader[0])
		chanNum = ord(channelHeader[2])
		appLogger.debug('Pre: {}'.format(self.toHexString(channelHeader)))
		name = self.readString()
		#channelNumber = ord(channelHeader[2])
		appLogger.debug('Channel: {}'.format(name))
		unit = self.readString()
		appLogger.debug('Unit: {}'.format(unit))
		blah = self.readString()
		appLogger.debug('Unit2: {}'.format(blah))
		# What follows is actually either 00:05:50:00 or 00:00:01:00:00:05:50:00 or 00:00:01:00:00:05:00:00
		# 00 or 50 indicates if the channel is calculated
		blah = self.readUntilDelimiter(chr(0x05))
		blah += self.fh.read(4)
		appLogger.debug('Blah2: {}'.format(self.toHexString(blah)))
		
		#chanNum, = struct.unpack('H', self.fh.read(2))
		#appLogger.debug('Channel number: {}'.format(chanNum))

		n, = struct.unpack('<i', self.fh.read(4))
		appLogger.debug('Length: {}'.format(n))
		# Create the channel info object
		chInfo = ChannelInfo(name = name, group = chanGroup, number = chanNum, unit = unit, start = self.fh.tell(), length = n)
		chInfo.computed = (channelHeader[0] == chr(0x50))
		
		self.fh.seek(16 * n, 1)
		
		blahEnd1 = self.fh.read(2)
		# Misterious 2 bytes that apperar sometimes, but always are 01:ff
		blahEnd2 = self.fh.read(2)
		if (blahEnd2 != '\x01\xff'):
			self.fh.seek(-2, 1)
		appLogger.debug('BlahEnd: {}'.format(self.toHexString(blahEnd1 + blahEnd2)))
		return chInfo

	def getChannelData(self, chInfo):
		dtype = np.dtype([('time', np.uint32), ('value', '<f8'), ('f3', '<f4')])
		arr = np.frombuffer(buffer(self.fh[chInfo.start: chInfo.start + 16 * chInfo.length]), dtype=dtype)
		return arr
	
	def findChannel(self, channelName, channelUnit):
		self.fh.seek(0)
		while True:
			titleLoc = self.fh.find(channelName)
			if (titleLoc == -1):
				raise ValueError("Channel {}(unit = {}) not found".format(channelName, channelUnit))
			self.fh.seek(titleLoc - 31)
			chInfo = self.getChannelInfo()
			if (chInfo.unit == channelUnit):
				break
			else:
				continue
		return chInfo
	
	def getChannelList(self):
		self.readHeader()
		chList = []
		while not self.checkEOF():
			chInfo = self.getChannelInfo()
			chList.append(chInfo)
			appLogger.debug(chInfo)
		return chList
	
def main1():
	_logConfigurator = SimpleAppLoggerConfgigurator('AMR Reader', logFile = False, debug = False)
	fileList = [
			'/data/Workspace/Django/SmoWeb/smotools/FatigueCalculations/work/InputFiles/140923.amr',
			'/data/Workspace/Django/SmoWeb/smotools/FatigueCalculations/work/InputFiles/150113hw_bg2.06+500+pt-zyklen_Liniendiagramm1_Zyklus223-228,6.amr',
			'/data/Workspace/Django/SmoWeb/smotools/FatigueCalculations/work/InputFiles/Bisheriger_schneller_2015erZyklus_50kgLH2.amr',
			'/data/Workspace/Django/SmoWeb/smotools/FatigueCalculations/work/InputFiles/Zyklenvariante_02_41kgLH2.amr',
	]
	for filePath in fileList:
		reader = AMRFileReader()
		reader.openFile(filePath)
		if True:
			try:
				chList = reader.getChannelList()
				for ch in chList:
					appLogger.info(ch)
			finally:
				appLogger.debug("Location: ".format(reader.fh.tell()))
		else:
			chInfo = reader.findChannel('P-Y-408', 'bar')
			r = reader.getChannelData(chInfo)
def main2():
	filePath = '/data/Workspace/Django/SmoWeb/smotools/FatigueCalculations/work/InputFiles/Zyklenvariante_02_41kgLH2.amr'
	reader = AMRFileReader()
	reader.openFile(filePath)
	chInfo1 = reader.findChannel('T_CFK_o_m', 'Ohm')
	chInfo2 = reader.findChannel('T_CFK_o_m', 'K')
	data1 = reader.getChannelData(chInfo1)
	data2 = reader.getChannelData(chInfo2)
	print data1[1800:2100]
	print('--------------------')
	print data2[0:300]
if __name__ == '__main__':
	main2()