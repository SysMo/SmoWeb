from smo.util import addKeyFieldToValues

Solids = {
	'StainlessSteel304' : {'label' : 'stainless steel 304', 
		'refValues' : {
			'density' : 7800
		}
	},
	'Aluminium6061' : {'label' : 'aluminium 6061',
		'refValues' : {
			'density' : 2700
		}
	}
}

addKeyFieldToValues(Solids)

Fluids = {
	"ParaHydrogen" : {'label' : "ParaHydrogen"},
	"OrthoHydrogen" : {'label' : "OrthoHydrogen"},
	"Hydrogen" : {'label' : "Hydrogen"},
	"Water" : {'label' : "Water"},
	"Air" : {'label' : "Air"},
	"Nitrogen" : {'label' : "Nitrogen"},
	"Oxygen" : {'label' : "Oxygen"},
	"CarbonDioxide" : {'label' : "CarbonDioxide"},
	"CarbonMonoxide" : {'label' : "CarbonMonoxide"},
	"R134a" : {'label' : "R134a"},
	"R1234yf" : {'label' : "R1234yf"},
	"R1234ze(Z)" : {'label' : "R1234ze(Z)"},
	"Ammonia" : {'label' : "Ammonia"},
	"Argon" : {'label' : "Argon"},
	"Neon" : {'label' : "Neon"},
	"Helium" : {'label' : "Helium"},
	"Methane" : {'label' : "Methane"},
	"Ethane" : {'label' : "Ethane"},
	"Ethylene" : {'label' : "Ethylene"},
	"n-Propane" : {'label' : "n-Propane"},
	"n-Butane" : {'label' : "n-Butane"},
	"IsoButane" : {'label' : "IsoButane"},
	"n-Pentane" : {'label' : "n-Pentane"},
	"Isopentane" : {'label' : "Isopentane"},
	"Methanol" : {'label' : "Methanol"},
	"Ethanol" : {'label' : "Ethanol"}
}

addKeyFieldToValues(Fluids)