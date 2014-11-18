from smo.util import addKeyFieldToValues
from collections import OrderedDict

Solids = OrderedDict((
	('Aluminium6061', {'label' : 'aluminium 6061',
		'refValues' : {
			'density' : 2700
		}
	}),
	('StainlessSteel304', {'label' : 'stainless steel 304', 
		'refValues' : {
			'density' : 7800
		}
	}),
))

addKeyFieldToValues(Solids)

Fluids = OrderedDict((
	("ParaHydrogen", "Hydrogen (para)"),
	("OrthoHydrogen", "Hydrogen (ortho)"),
	("Hydrogen", "Hydrogen (normal)"),
	("Water", "Water"),
	("Air", "Air"),
	("Nitrogen", "Nitrogen"),
	("Oxygen", "Oxygen"),
	("CarbonDioxide", "Carbon dioxide"),
	("CarbonMonoxide", "Carbon monoxide"),
	("R134a", "R134a"),
	("R1234yf", "R1234yf"),
	("R1234ze(Z)", "R1234ze(Z)"),
	("Ammonia", "Ammonia"),
	("Argon", "Argon"),
	("Neon", "Neon"),
	("Helium", "Helium"),
	("Methane", "Methane"),
	("Ethane", "Ethane"),
	("Ethylene", "Ethylene"),
	("n-Propane", "n-Propane"),
	("n-Butane", "n-Butane"),
	("IsoButane", "IsoButane"),
	("n-Pentane", "n-Pentane"),
	("Isopentane", "Isopentane"),
	("Methanol", "Methanol"),
	("Ethanol", "Ethanol")
))