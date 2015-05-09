'''
Created on Nov 7, 2013

@author: Atanas Pavlov
'''

import struct
import datetime
import os, sys
import re
import numpy as np
os.environ['ETS_TOOLKIT'] = 'qt4'

import traits.api as T
import traitsui.api as TUI
import traitsui.table_column as TCol
from pyface.qt import QtGui, QtCore


class DataRecordDefinition(T.HasTraits):
	types = T.List(T.Int) # 0 - UInt, 1 - Int, 2,3 - Float, 7 - string
	sizeList = T.List(T.Int)
	positionByteList = T.List(T.Int)
	positionOffsetList = T.List(T.Int)
	def addChannel(self, dataType, initialPosition, dataSize):
		self.types.append(dataType)
		self.sizeList.append(dataSize)
		self.positionByteList.append(initialPosition // 8)
		self.positionOffsetList.append(initialPosition % 8)
	
	def getValue(self, record, channelIndex, structFmt):
		thisByte = self.positionByteList[channelIndex]
		thisOffset = self.positionOffsetList[channelIndex]
		thisSize = self.sizeList[channelIndex]
		if (thisSize < 8):
			mask = np.sum(2**np.arange(thisSize) << thisOffset)
			result = struct.unpack('B', record[thisByte])[0] & mask
		else:
			result = struct.unpack(structFmt, record[thisByte:(thisByte + thisSize//8)])[0]
		return result

	def parseRecord(self, record):
		result = []
		for i in range(len(self.types)):
			value = None
			thisType = self.types[i]
			thisSize = self.sizeList[i]
			# Real
			if (thisType == 2 or thisType == 3):
				if (thisSize == 32):
					value = self.getValue(record, i, 'f')
				elif (thisSize == 64):
					value = self.getValue(record, i, 'd')
			# Unsigned integer
			elif (thisType == 0):
				if (thisSize == 8):
					value = self.getValue(record, i, 'B')
				elif (thisSize == 16):
					value = self.getValue(record, i, 'H')
				elif (thisSize == 32):
					value = self.getValue(record, i, 'I')
				elif (thisSize < 8):
					value = self.getValue(record, i, None)
			# Signed integer
			elif (thisType == 1):
				if (thisSize == 8):
					value = self.getValue(record, i, 'b')
				elif (thisSize == 16):
					value = self.getValue(record, i, 'h')
				elif (thisSize == 32):
					value = self.getValue(record, i, 'i')
				elif (thisSize < 8):
					value = self.getValue(record, i, None)
				
			result.append(value)
		return result
				
class ConversionFormula:
	def __init__(self, conversionFormulaType, parameters):
		self.parameters = parameters
		self.conversionFormulaType = conversionFormulaType
		if (conversionFormulaType == 0):
			self.conversionFunction = self.parametricLinearConversion
		else:
			raise ValueError ("Invalid conversion formula type %d"%conversionFormulaType)
	
	def parametricLinearConversion(self, channelValues):
		return self.parameters[0] + self.parameters[1] * channelValues
	
	def __call__(self, channelValues):
		return self.conversionFunction(channelValues)
	
	def getRepr(self):
		if (self.conversionFormulaType == 0):
			s = "y = %e + %e * x"%(self.parameters)
		return s

class SignalChannel(T.HasTraits):
	name = T.Str
	description = T.Str
	firstBit = T.Int
	numberBits = T.Int
	signalType = T.Int
	samplingRate = T.Float
	data = T.Array
	unit = T.Str
	conversionFormula = T.Instance(ConversionFormula) 
	 
	def getRepr(self):		
		if (self.conversionFormula != None):
			conversionFormulaStr = ",\n\tunit = '%s', conversionFormula = '%s'"% \
			(self.unit, self.conversionFormula.getRepr())
		else:
			conversionFormulaStr = ""
		s = \
"""SignalChannel(name = '%s', description = '%s', 
	firstBit = %d, numberBits = %d, signalType = %d, samplingRate = %f[s]%s
)"""\
			%(self.name, self.description, self.firstBit, self.numberBits, 
			self.signalType, self.samplingRate, conversionFormulaStr)
		return s


class ChannelGroup(T.HasTraits):
	channels = T.List(SignalChannel)
	dataRecordDefinition = T.Instance(DataRecordDefinition)
	recordId = T.Int
	recordSize = T.Int
	numberRecords = T.Int

		
	def getRepr(self):
		s = 'ChannelGroup(recordId = %d, numberChannels = %d, recordSize = %d, numberRecords = %d)'\
			%(self.recordId, len(self.channels), self.recordSize, self.numberRecords)
		return s
	
class DataGroup(T.HasTraits):
	channelGroups = T.List(ChannelGroup)
	numberRecordIds = T.Int
	
	def getRepr(self):
		s = "DataGroup(nuberRecordIds = %d)"%self.numberRecordIds
		return s
	
	def readFromMat(self, f, dataBeginAddress):
		for channelGroup in self.channelGroups:
			for channel in channelGroup.channels:
				channel.data = np.zeros((channelGroup.numberRecords,))

			for i in range(channelGroup.numberRecords):
				recordBegin = dataBeginAddress + i * channelGroup.recordSize;
				f.seek(recordBegin)
				recordRawData = f.read(channelGroup.recordSize) 				
				recordData = channelGroup.dataRecordDefinition.parseRecord(recordRawData)
				j = 0
				for channel in channelGroup.channels:
					if (channel.conversionFormula != None):
						channel.data[i] = channel.conversionFormula(recordData[j])
					else:
						channel.data[i] = recordData[j]
					j += 1
			
class MDFFileReader:
	currentDataGroup = None
	currentChannelGroup = None
	currentChannel = None
	def __init__(self, inputFileName):
		self.inputFileName = inputFileName
		self.f = open(inputFileName, 'rb')
		
	def readChunk(self, chunkFormat):
		chunkSize = struct.calcsize(chunkFormat)
		rawData = self.f.read(chunkSize)
		data = struct.unpack(chunkFormat, rawData)
		return data
	
	def readIDBlock(self):
		headerBlockStruct = '<8s8s8sHHHH2s30s'
		print(self.readChunk(headerBlockStruct))
	
	def readHeaderBlock(self):
		blockTypeCode, blockSize = self.readChunk('2sH')
		headerBlockStruct = '<iiiH10s8s32s32s32s32s'
		data = self.readChunk(headerBlockStruct)
		groupBlockOffset = data[0]
		self.f.seek(groupBlockOffset)
	
	def readDataGroupBlock(self):
		blockTypeCode, blockSize = self.readChunk('2sH')
		blockStruct = '<iiiiHIH'
		data = self.readChunk(blockStruct)
		self.currentDataGroup = DataGroup() 
		self.dataGroups.append(self.currentDataGroup)
		self.currentDataGroup.numberRecordIds = data[5]
		assert(self.currentDataGroup.numberRecordIds == 0)
		assert(data[4] == 1) # Only one channel group allowed
		nextGroup = data[0]
		dataRecordsAddress = data[3]
		firstChannelGroupAddress = data[1]
		print(self.currentDataGroup.getRepr())
		
		if (firstChannelGroupAddress != 0):
			self.f.seek(firstChannelGroupAddress)
			hasMore = True
			while hasMore:
				hasMore = self.readChannelGroupBlock()
		self.currentDataGroup.readFromMat(self.f, dataRecordsAddress)
		
		if (nextGroup == 0):
			return False
		else:
			self.f.seek(nextGroup)
			return True
	
	def readChannelGroupBlock(self):
		blockTypeCode, blockSize = self.readChunk('2sH')
		blockStruct = '<iiiHHHI'
		data = self.readChunk(blockStruct)
		self.currentChannelGroup = ChannelGroup() 
		self.currentDataGroup.channelGroups.append(self.currentChannelGroup)
		self.currentChannelGroup.recordId = data[3]
		#self.currentChannelGroup.numberChannels = data[4]
		self.currentChannelGroup.recordSize = data[5]
		self.currentChannelGroup.numberRecords = data[6]
		self.currentChannelGroup.dataRecordDefinition = DataRecordDefinition()
		nextChannelGroup = data[0]
		firstChannelAddress = data[1]
		
		if (firstChannelAddress != 0):
			self.f.seek(firstChannelAddress)
			hasMore = True
			while hasMore:
				hasMore = self.readChannelBlock()

		print(self.currentChannelGroup.getRepr())

		if (nextChannelGroup == 0):
			return False
		else:
			self.f.seek(nextChannelGroup)
			return True

	def readChannelBlock(self):
		blockTypeCode, blockSize = self.readChunk('2sH')
		assert(blockTypeCode == 'CN')
		blockStruct = '<iiiiiH32s128sHHHHdddii'
		data = self.readChunk(blockStruct)
		channel = SignalChannel()
		self.currentChannel = channel
		self.currentChannelGroup.channels.append(channel)
		
		# Read channel attrubutes
		channelName = self.getString(data[6])
		m = re.search("[A-Za-z0-9_-]*", channelName)
		assert(m is not None)
		channel.name = m.group(0) 
		channel.description = self.getString(data[7])
		channel.firstBit = data[8]
		channel.numberBits = data[9]
		channel.signalType = data[10]
		channel.samplingRate = data[11]
		
		# Read and return conversion formula 
		if(data[1] != 0):
			msg = "Channel '%s' has conversion formula"%channel.name
			print(msg)
			self.f.seek(data[1])
			channel.unit, channel.conversionFormula = self.readConversionFormula()

		
		self.currentChannelGroup.dataRecordDefinition.addChannel(
			channel.signalType, channel.firstBit, channel.numberBits
		)

		print(self.currentChannel.getRepr())

		nextChannel = data[0]
		
		if (nextChannel == 0):
			return False
		else:
			self.f.seek(nextChannel)
			return True

	def readConversionFormula(self):
		blockTypeCode, blockSize = self.readChunk('2sH')
		assert(blockTypeCode == 'CC')
		blockStruct = '<hdd20sHH'
		data = self.readChunk(blockStruct)
		unit = self.getString(data[3])
		formulaType = data[4]
		numberParameters = data[5]
		
		conversionFormula = None
		import warnings
		if (formulaType == 0):
			blockStruct = 'd' * numberParameters
			parameters = self.readChunk(blockStruct)
			conversionFormula = ConversionFormula(0, parameters)
		elif (formulaType == 65535):
			# One-to-one conversion (value to physical unit)
			conversionFormula = None
		else:
			msg = "Untranslated conversionFormula (unit = '%s', formulaType = %d, numberParameters = %d)" % \
			(unit, formulaType, numberParameters)
			warnings.warn(msg)
		
		return unit, conversionFormula
	
	def readText(self):
		blockTypeCode, blockSize = self.readChunk('2sH')
		text = self.readChunk('%ds'%(blockSize - 4))
		return text
	
	def getString(self, data):
		return re.sub(r'[\x00]', '', data)
		
	def read(self):
		self.readIDBlock()
		self.readHeaderBlock()
		self.dataGroups = []
		hasMore = True
		while hasMore:
			hasMore = self.readDataGroupBlock()			
		return self.dataGroups
	
	def saveAsMat(self, outputFileName, resample = False):
		from scipy.io import savemat
		groupNumber = 0
		groupDict = {}
		resamplingInterval = 0.025
		for dataGroup in self.dataGroups: 
			for channelGroup in dataGroup.channelGroups:
				if (channelGroup.numberRecords > 50):
					time = None
					# Get the original and resampling time
					for i in range(len(channelGroup.channels)):
						if (channelGroup.channels[i].name == 'time'):
							timeChannel = channelGroup.channels.pop(i)
							time = timeChannel.data
							resamplingTime = np.arange(time[0], time[-1], resamplingInterval)
							break
					assert (time is not None)
					# Create group name
					groupNumber += 1
					groupName = "group%d"%groupNumber
					if (resample):
						channelGroupDict = {"time" : resamplingTime}
					else:
						channelGroupDict = {"time" : time}
					groupDict[groupName] = channelGroupDict
					# Resample the non-zero channels 
					for channel in channelGroup.channels:
						name = channel.name
						if (len(name) > 31):
							name = name[:31]
						if (np.any(channel.data)):
							if (resample):
								channel.data = np.interp(resamplingTime, time, channel.data)
							channelGroupDict[name] = channel.data
						else:
							#channel.data = np.zeros((1,))
							pass
		
		savemat(outputFileName, groupDict)

	def saveAsHDF5(self, outputFileName):
		import h5py
		groupNumber = 0
		f = h5py.File(outputFileName, "w")
		for dataGroup in self.dataGroups: 
			for channelGroup in dataGroup.channelGroups:
				if (channelGroup.numberRecords > 50):
					# Create group name
					groupNumber += 1
					groupName = "group%d"%groupNumber
					print("Writing group '%s'"%groupName)
					group = f.create_group(groupName)
					for channel in channelGroup.channels:
						name = channel.name
						if (len(name) > 31):
							name = name[:31]
						if (np.any(channel.data) and (name not in group)):
							print("Writing channel '%s'"%name)
							group.create_dataset(name, shape = channel.data.shape, 
								dtype = channel.data.dtype, data = channel.data)
		f.close()

	
def main():
	import glob
	import os.path
	basePath = "/data/tmp/DDP/"
	#dataPath = "2013_11_06_Rolle"
	#dataPath = "2013_11_23_ET Hyptek_Kasterl"
	#dataPath = "2013_11_21_ET"
	#dataPath = "2013_11_20_ET Stromtest_2/Highside switching"
	#dataPath = "2013_11_20_ET Stromtest_2/Push Pull switching"
	#dataPath = "2013_11_27_Skyfall Rolle bis 42KW"
	#dataPath = "2013_11_28_Hyptek_Kasterl_im_Skyfall"
	#dataPath = "2013_11_28_Skyfall Rolle bis 37KW"
	#dataPath = "2013_11_29_Skyfall Rolle"
	dataPath = "2013_12_02_Skyfall Aschheim"

	pathList = glob.glob(os.path.join(basePath, dataPath,"*.dat"))
	
	for filePath in pathList:
		inputFileName = filePath
		print ("Converting file '%s'"%inputFileName)
		mdf = MDFFileReader(inputFileName)
		mdf.read()

		outputFileName = os.path.splitext(filePath)[0] + '.hdf'
		#mdf.saveAsMat(outputFileName)
		mdf.saveAsHDF5(outputFileName)
	
main()