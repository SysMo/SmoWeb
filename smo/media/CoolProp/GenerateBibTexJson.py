'''
Created on Nov 25, 2014

@author: Atanas Pavlov
'''

import bibtexparser
import json

with open('CoolPropBibTeXLibrary.bib') as bibtexFile:
	content = bibtexFile.read()
	
bibDatabase = bibtexparser.loads(content)

jsonContent = json.dumps(bibDatabase.entries_dict, indent = 4)

with open('CoolPropReferences.py', 'w') as outFile:
	outFile.write('References = \\\n')
	outFile.write(jsonContent)
	