from smo.util import addKeyFieldToValues
from collections import OrderedDict

Solids = OrderedDict((
	('Aluminium6061', {'label' : 'aluminium 6061',
		'refValues' : {
			'density' : 2700.
		},
		'thermalCond_T': {
			'T': [20.0 , 50.0 , 75.0 , 100.0 , 125.0 , 150.0 , 175.0 , 200.0 , 225.0 , 250.0 , 275.0 , 300.0],
			'cond': [28.47 , 62.14 , 82.26 , 97.84 , 110.31 , 120.54 , 129.05 , 136.22 , 142.3 , 147.46 , 151.84 , 155.54],
		},
		'heatCapacity_T': {
			'T': [20.0 , 50.0 , 75.0 , 100.0 , 125.0 , 150.0 , 175.0 , 200.0 , 225.0 , 250.0 , 275.0 , 300.0],
			'cp': [8.85 , 148.84 , 334.15 , 492.2 , 616.63 , 713.03 , 784.783 , 835.24 , 869.61 , 895.04 , 920.01 , 953.86],
		},
	}),
	('StainlessSteel304', {'label' : 'stainless steel 304', 
		'refValues' : {
			'density' : 7800.
		},
		'thermalCond_T': {
			'T': [20.0 , 50.0 , 75.0 , 100.0 , 125.0 , 150.0 , 175.0 , 200.0 , 225.0 , 250.0 , 275.0 , 300.0, 400.0],
			'cond': [1.95, 5.8, 7.94, 9.4, 10.6, 11.5, 12.3, 13, 13.6, 14.1, 14.5, 14.9, 14.9],
		},
		'heatCapacity_T': {
			'T': [20.0 , 50.0 , 75.0 , 100.0 , 125.0 , 150.0 , 175.0 , 200.0 , 225.0 , 250.0 , 275.0 , 300.0],
			'cp': [12.6, 100, 182, 250, 300, 347, 388, 419, 432, 439, 445, 477],
		},
		'emissivity_T':{
			'unfinishedSurface': { 
				'T': [0, 20.0, 40.0, 80.0, 120.0, 200.0, 300.0, 400],
				'epsilon': [0, 0.023, 0.036, 0.051, 0.064, 0.0985, 0.1385, 0.1385]
			},
		},
	}),
	('CarbonFiberComposite', {
		'refValues' : {
			'density' : 2700.
		},
		'thermalCond_T': {
			'T': [20.0 , 50.0 , 75.0 , 100.0 , 125.0 , 150.0 , 175.0 , 200.0 , 225.0 , 250.0 , 275.0 , 300.0, 400.0],
			'cond': [0.06, 0.19, 0.31, 0.42, 0.51, 0.58, 0.63, 0.66, 0.68, 0.69, 0.7, 0.71],
		},
		'heatCapacity_T': {
			'T': [20.0 , 50.0 , 75.0 , 100.0 , 125.0 , 150.0 , 175.0 , 200.0 , 225.0 , 250.0 , 275.0 , 300.0],
			'cp': [0.05, 75.53, 197.91, 309.65, 410.77, 501.26, 581.13, 650.38, 709.0, 757.0, 794.36, 821.11],
		},
	}),
	('Copper', {'label': 'copper (pure)',
		'refValues': {
			'density': 8960.,
			'eResistivity': 16.78e-9,
			'eConductivity': 5.96e7,
			'cp':  385.,
			'tConductivity': 401.
		}
	}),
	('Polyoxymethylene', {'label': 'polyoxymethylene (POM)', 
		'refValues': {
			'density': 1420,
			'tConductivity': 0.23,
			'cp': 1500.
		}	
	}),
	('Polyvinylchloride', {'label': 'polyvinylchloride (PVC)',
		'refValues': {
			'tConductivity': 0.19
		}
	})
))

addKeyFieldToValues(Solids)

Fluids = OrderedDict((
	("Acetone", "Acetone"),
	("Air", "Air"),
	("Ammonia", "Ammonia"),
	("Argon", "Argon"),
	("Benzene", "Benzene"),
	("IsoButane", "iso-Butane"),
	("n-Butane", "n-Butane"),
	("cis-2-Butene", "cis-2-Butene"),
	("trans-2-Butene", "trans-2-Butene"),
	("IsoButene", "iso-Butene"),
	("1-Butene", "1-Butene"),
	("CarbonDioxide", "Carbon dioxide"),
	("CarbonMonoxide", "Carbon monoxide"),
	("CarbonylSulfide", "Carbonyl sulfide"),
	("n-Decane", "n-Decane"),
	("Deuterium", "Deuterium"),
	("OrthoDeuterium", "ortho-Deuterium"),
	("ParaDeuterium", "para-Deuterium"),
	("DimethylCarbonate", "Dimethyl carbonate"),
	("DimethylEther", "Dimethyl ether"),
	("n-Dodecane", "n-Dodecane"),
	("D4", "D4"),
	("D5", "D5"),
	("D6", "D6"),
	("Ethane", "Ethane"),
	("Ethanol", "Ethanol"),
	("Ethylene", "Ethylene"),
	("EthylBenzene", "Ethyl benzene"),
	("Fluorine", "Fluorine"),
	("Helium", "Helium"),
	("CycloHexane", "cyclo-Hexane"),
	("Isohexane", "iso-Hexane"),
	("n-Hexane", "n-Hexane"),
	("n-Heptane", "n-Heptane"),
	("HFE143m", "HFE143m"),
	("Hydrogen", "normal-Hydrogen"),
	("OrthoHydrogen", "ortho-Hydrogen"),
	("ParaHydrogen", "para-Hydrogen"),
	("HydrogenSulfide", "Hydrogen sulfide"),
	("Krypton", "Krypton"),
	("Methane", "Methane"),
	("Methanol", "Methanol"),
	("MethylLinoleate", "Methyl linoleate"),
	("MethylLinolenate", "Methyl linolenate"),
	("MethylOleate", "Methyl oleate"),
	("MethylPalmitate", "Methyl palmitate"),
	("MethylStearate", "Methyl stearate"),
	("MD2M", "MD2M"),
	("MD3M", "MD3M"),
	("MD4M", "MD4M"),
	("MDM", "MDM"),
	("MM", "MM"),
	("Neon", "Neon"),
	("Nitrogen", "Nitrogen"),
	("NitrousOxide", "Nitrous oxide"),
	("n-Nonane", "n-Nonane"),
	("n-Octane", "n-Octane"),
	("Oxygen", "Oxygen"),
	("Cyclopentane", "cyclo-Pentane"),
	("Isopentane", "iso-Pentane"),
	("n-Pentane", "n-Pentane"),
	("Neopentane", "neo-Pentane"),
	("CycloPropane", "cyclo-Propane"),
	("n-Propane", "n-Propane"),
	("Propylene", "Propylene"),
	("Propyne", "Propyne"),
	("R11", "R11"),
	("R113", "R113"),
	("R114", "R114"),
	("R116", "R116"),
	("R12", "R12"),
	("R123", "R123"),
	("R1233zd(E)", "R1233zd(E)"),
	("R1234yf", "R1234yf"),
	("R1234ze(E)", "R1234ze(E)"),
	("R1234ze(Z)", "R1234ze(Z)"),
	("R124", "R124"),
	("R125", "R125"),
	("R13", "R13"),
	("R134a", "R134a"),
	("R14", "R14"),
	("R141b", "R141b"),
	("R142b", "R142b"),
	("R143a", "R143a"),
	("R152A", "R152A"),
	("R161", "R161"),
	("R161", "R161"),
	("R21", "R21"),
	("R218", "R218"),
	("R22", "R22"),
	("R227EA", "R227EA"),
	("R23", "R23"),
	("R236EA", "R236EA"),
	("R236FA", "R236FA"),
	("R245fa", "R245fa"),
	("R32", "R32"),
	("R365MFC", "R365MFC"),
	("R41", "R41"),
	("RC318", "RC318"),
	("SulfurDioxide", "SulfurDioxide"),
	("SulfurHexafluoride", "SulfurHexafluoride"),
	("Toluene", "Toluene"),
	("n-Undecane", "n-Undecane"),
	("Water", "Water"),
	("Xenon", "Xenon"),
	("m-Xylene", "m-Xylene"),
	("o-Xylene", "o-Xylene"),
	("p-Xylene", "p-Xylene"),
))
