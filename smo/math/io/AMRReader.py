import numpy as np
import struct
from smo.util.log import SimpleAppLoggerConfgigurator
import mmap
import logging

appLogger = logging.getLogger('AppLogger')

filename = '140923.amr'
initOffset = 346

class ChannelInfo(object):
	def __init__(self, name, unit, start, length):
		self.name = name
		self.unit = unit
		self.start = start
		self.length = length
	
	def __str__(self):
		return "{}(unit = {}, start = {}, length = {})".format(self.name, self.unit, self.start, self.length)

class AMRReader(object):
	def openFile(self, filePath, offset = 0):
		self.filePath = filePath
		f = open(filePath, 'r')
		self.fh = mmap.mmap(f.fileno(), 0, access = mmap.ACCESS_READ)
		self.fh.seek(offset, 0)
	
	def __del__(self):
		self.fh.close()
	
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
		blah = self.readString()
		appLogger.info(blah)
		self.fh.seek(initOffset)
	
	def getChannelInfo(self):
		# This is something like
		# 00:00:19:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:01:00:03:00:80:80:80:00:02:00:00:00
		# byte 1 is 0 for measurements, 50 for calculations
		# byte 3 is the channel number
		channelHeader = self.fh.read(30)
		appLogger.info('Pre: {}'.format(self.toHexString(channelHeader)))
		name = self.readString()
		appLogger.info('Channel: {}'.format(name))
		unit = self.readString()
		appLogger.info('Unit: {}'.format(unit))
		blah = self.readString()
		appLogger.info('Unit2: {}'.format(blah))
		# What follows is actually either 00:05:50:00 or 00:00:01:00:00:05:50:00 or 00:00:01:00:00:05:00:00
		# 00 or 50 indicates if the channel is calculated
		blah = self.readUntilDelimiter(chr(0x05))
		blah += self.fh.read(2)
		appLogger.info('Blah2: {}'.format(self.toHexString(blah)))
		chanNum, = struct.unpack('H', self.fh.read(2))
		appLogger.info('Channel number: {}'.format(chanNum))
		n, = struct.unpack('<i', self.fh.read(4))
		appLogger.info('Length: {}'.format(n))
		
		# Create the channel info object
		chInfo = ChannelInfo(name = name, unit = unit, start = self.fh.tell(), length = n)
		chInfo.computed = (channelHeader[0] == chr(0x50))
		
		self.fh.seek(16 * n, 1)
		blahEnd1 = self.fh.read(2)
		# Misterious 2 bytes that apperar sometimes, but always are 01:ff
		blahEnd2 = self.fh.read(2)
		if (blahEnd2 != '\x01\xff'):
			self.fh.seek(-2, 1)
		appLogger.info('BlahEnd: {}'.format(self.toHexString(blahEnd1 + blahEnd2)))
		appLogger.info(chInfo)
		return chInfo

	def getChannelData(self, chInfo):
		dtype = np.dtype([('f1', 'i4'), ('f2', '<f8'), ('f3', 'i4')])
		#fp = np.memmap(filename, dtype=dtype, mode='r', shape = (length,), offset = self.fh.tell())
		#return fp['f2'].copy()
		arr = np.frombuffer(buffer(self.fh[chInfo.start: chInfo.start + 16 * chInfo.length]), dtype=dtype)
		return arr['f2']
	
	def findChannel(self, channelName, channelUnit):		
		currPos = 0
		while True:
			titleLoc = self.fh.find(channelName)
			if (titleLoc == -1):
				raise ValueError("Channel {}(unit = {}) not found".format(channelName, channelUnit))
			self.fh.seek(titleLoc - 31)
			print self.fh.tell()
			chInfo = self.getChannelInfo()
			if (chInfo.unit == channelUnit):
				break
			else:
				continue
		return chInfo
 

def main():
	_logConfigurator = SimpleAppLoggerConfgigurator('AMR Reader', logFile = False)
	appLogger.info('Begin')
	reader = AMRReader()
	reader.openFile(filename, initOffset)
	chInfo = reader.findChannel('P-Y-408', 'bar')
	print reader.getChannelData(chInfo)
	#reader.readHeader()
# 	print reader.fh.tell()
# 	while reader.fh.read(4) != '\x00\x00\x00\xFF':
# 		reader.fh.seek(-4, 1)
# 		print reader.fh.tell()
# 		reader.getChannelInfo()
main()