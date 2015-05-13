'''
Created on Sep 17, 2014

@author: ivaylo
'''
import glob
import os
import json
from decimal import Decimal
import uuid
import time

def genTimestampUUID():
	return time.strftime('%Y%m%d_%H%M%S', time.gmtime()) + '_' + uuid.uuid4().hex

def handle_uploaded_file(f, media_path):
	destination = open(os.path.join(media_path, f.name), 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()
	return destination



class TemporaryObjectsHash:
	def __init__(self, klass = object):
		self.klass = klass
		self.collection = {}
		
	def push(self, obj, key = None):
		if (not isinstance(obj, self.klass)):
			raise TypeError('Attempt to add self of type ' + type(obj)
					+ ' to collection of type ' + self.klass)
		if (key == None):
			key = uuid.uuid4().hex
		self.collection[key] = obj
		return key
	
	def get(self, key):
		return self.collection.get(key)
	
	def pop(self, key):
		return self.collection.pop(key)

class DecimalEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Decimal):
			return float(obj)
		return json.JSONEncoder.default(self, obj)
	# Output has one decimal, change format if you need more
	# json.encoder.FLOAT_REPR = lambda o: format(o, '.1f')
	
	# Usage:
	# d = Decimal("42.5")
	# json.dumps(d, cls=DecimalEncoder)

import time
from datetime import timedelta	
def clearOldFiles(dir, timePeriod = timedelta(days = 1)):
	"""
	Deletes files older than ...
	"""
	timePeriod_inSec = timePeriod.total_seconds()
	for file in glob.glob(os.path.join(dir, '*.*')):
		currentTime = time.time()
		fileCreationTime = os.path.getctime(file)
		if currentTime - fileCreationTime > timePeriod_inSec:
			os.remove(file)
		
	