'''
Created on Sep 17, 2014

@author: ivaylo
'''
import csv
import numpy as np
import glob
import os
import json
from django.db.utils import OperationalError
from decimal import Decimal

def handle_uploaded_file(f, media_path):
	destination = open(os.path.join(media_path, f.name), 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()
	return destination


import uuid
class TemporaryObjectsHash:
	def __init__(self, klass = object):
		self.klass = klass
		self.collection = {}
		
	def push(self, instance, key = None):
		if (not isinstance(instance, self.klass)):
			raise TypeError('Attempt to add instance of type ' + type(instance)
					+ ' to collection of type ' + self.klass)
		if (key == None):
			key = uuid.uuid4().hex
		self.collection[key] = instance
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
