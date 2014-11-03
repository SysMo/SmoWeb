def addKeyFieldToValues(dictObj):
	for key, value in dictObj.iteritems():
		value['_key'] = key
