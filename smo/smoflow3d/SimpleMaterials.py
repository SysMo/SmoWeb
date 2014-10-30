Solids = {
	'StainlessSteel304' : {'title' : 'stainless steel 304', 
		'refValues' : {
			'density' : 7800
		}
	},
	'Aluminium6061' : {'title' : 'aluminium 6061',
		'refValues' : {
			'density' : 2700
		}
	}
}
def getSolidDictList():
	solidDictList = {key : {'title' : value['title']} for (key, value) in Solids.iteritems() }
	return solidDictList

if __name__ == '__main__':
	print getSolidDictList()