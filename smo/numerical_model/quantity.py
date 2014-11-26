from collections import OrderedDict
Quantities = {
	'Dimensionless' : {'title' : 'dimensionless quantity', 'nominalValue' : 1, 'SIUnit' : '-', 
			'units' : OrderedDict((('-', {'mult' : 1}),))},
	'Length' : {'title' : 'length', 'nominalValue' : 1, 'SIUnit' : 'm', 
		'units' : OrderedDict((('m', {'mult' : 1}), ('km', {'mult' : 1e3}), ('cm', {'mult' : 1e-2}), ('mm', {'mult' : 1e-3}), 
		('um', {'mult' : 1e-6}), ('nm', {'mult' : 1e-9}), ('in', {'mult' : 2.54e-2}), ('ft', {'mult' : 3.048e-1}), ('yd', {'mult' : 0.9144}), ('mi', {'mult' : 1609.344}),))},
	'Area' : {'title' : 'area', 'nominalValue' : 1, 'SIUnit' : 'm**2', 
		'units' : {'m**2' : {'mult' : 1}, 'cm**2' : {'mult' : 1e-4}, 'mm**2' : {'mult' : 1e-6}}},
	'Volume' : {'title' : 'volume', 'nominalValue' : 1, 'SIUnit' : 'm**3', 
		'units' : OrderedDict((('m**3', {'mult' : 1}), ('L', {'mult' : 1e-3}), ('cm**3', {'mult' : 1e-6}), ('mm**3', {'mult' : 1e-9}),))},
	'Time' : {'title' : 'time', 'nominalValue' : 1, 'SIUnit' : 's', 
		'units' : OrderedDict((('s', {'mult' : 1}), ('ms', {'mult' : 1e-3}), ('us', {'mult' : 1e-6}), ('min', {'mult' : 60}), ('h', {'mult' : 3600}), ('day', {'mult' : 8.64e4}), ('year', {'mult' : 3.15576e7}),))},
	'Force' : {'title' : 'force', 'nominalValue' : 1, 'SIUnit' : 'N', 
		'units' : OrderedDict((('N', {'mult' : 1}), ('kN', {'mult' : 1e3}), ('MN', {'mult' : 1e6}), ('lb', {'mult' : 4.44822162825}),))},
	'Weight' : {'title' : 'weight', 'nominalValue' : 1, 'SIUnit' : 'N', 
		'units' : OrderedDict((('N', {'mult' : 1}), ('kN', {'mult' : 1e3}), ('MN', {'mult' : 1e6}), ('kgf', {'mult' : 9.80665}), ('gf', {'mult' : 9.80665e-3}), ('tf', {'mult' : 9.80665e+3}), ('lb', {'mult' : 4.44822162825}), ('oz', {'mult' : 0.278013851766}),))},
	'Velocity' : {'title' : 'velocity', 'nominalValue' : 1, 'SIUnit' : 'm/s', 
			'units' : OrderedDict((('m/s', {'mult' : 1}), ('km/h', {'mult' : 1/3.6}), ('km/s', {'mult' : 1e3}), ('mm/s', {'mult' : 1e-3}),))},
	'Mass' : {'title' : 'mass', 'nominalValue' : 1, 'SIUnit' : 'kg', 
		'units' : OrderedDict((('kg', {'mult' : 1}), ('g', {'mult' : 1e-3}), ('ton', {'mult' : 1e3}),))},
	'MolarMass' : {'title' : 'molar mass', 'nominalValue' : 1e-3, 'SIUnit' : 'kg/mol', 'defDispUnit' : 'g/mol',
		'units' : OrderedDict((('kg/mol', {'mult' : 1}), ('g/mol', {'mult' : 1e-3}),))},
	'Energy' : {'title' : 'energy', 'nominalValue' : 1, 'SIUnit' : 'J', 'defDispUnit' : 'kJ',
		'units' : OrderedDict((('J', {'mult' : 1}), ('kJ', {'mult' : 1e3}), ('MJ', {'mult' : 1e6}), ('GJ', {'mult' : 1e9}), ('Cal', {'mult' : 4.184}), ('kCal', {'mult' : 4.184e3}),
		('Wh', {'mult' : 3.6e3}),  ('kWh', {'mult' : 3.6e6}),  ('MWh', {'mult' : 3.6e9}), ('BTU', {'mult' : 1055}), ('eV', {'mult' : 1.60217657e-19}),))},
	'Power' : {'title' : 'power', 'nominalValue' : 1e3, 'SIUnit' : 'W', 'defDispUnit' : 'kW',
		'units' : OrderedDict((('W', {'mult' : 1}), ('kW', {'mult' : 1e3}), ('MW', {'mult' : 1e6}), ('GW', {'mult' : 1e9}),
		('mW', {'mult' : 1e-3}),  ('uW', {'mult' : 1e-6}),  ('hp', {'mult' : 746.0}), ('BTU/h', {'mult' : 0.293}),))},
	'HeatFlowRate' : {'title' : 'heat flow rate', 'nominalValue' : 1e3, 'SIUnit' : 'W', 'defDispUnit' : 'kW',
		'units' : OrderedDict((('W', {'mult' : 1}), ('kW', {'mult' : 1e3}), ('MW', {'mult' : 1e6}), ('GW', {'mult' : 1e9}),
		('mW', {'mult' : 1e-3}),  ('uW', {'mult' : 1e-6}),  ('hp', {'mult' : 746.0}), ('BTU/h', {'mult' : 0.293}),))},
	'Pressure' : {'title' : 'pressure', 'nominalValue' : 1e5, 'SIUnit' : 'Pa', 'defDispUnit' : 'bar',
		'units' : OrderedDict((('Pa', {'mult' : 1}), ('kPa', {'mult' : 1e3}), ('MPa', {'mult' : 1e6}), ('GPa', {'mult' : 1e9}), 
			('bar', {'mult' : 1e5}), ('psi', {'mult' : 6.89475e3}), ('ksi', {'mult' : 6.89475e6}), ('kN/m**2', {'mult' : 1e3}), ('kN/cm**2', {'mult' : 1e7}), ('kN/mm**2', {'mult' : 1e9}),))},
	'Temperature' : {'title' : 'temperature', 'nominalValue' : 273.15, 'SIUnit' : 'K', 
		'units' : OrderedDict((('K', {'mult' : 1}), ('degC', {'mult' : 1, 'offset' : 273.15}), ('degF', {'mult' : 5./9, 'offset' : 255.372222222222}),))},
	'Density' : {'title' : 'density', 'nominalValue' : 1, 'SIUnit' : 'kg/m**3', 
		'units' : OrderedDict((('kg/m**3', {'mult' : 1}), ('g/L', {'mult' : 1}), ('g/cm**3', {'mult' : 1e3}),))},
	'SpecificEnergy' : {'title' : 'specific energy', 'nominalValue' : 1e6, 'SIUnit' : 'J/kg', 'defDispUnit' : 'kJ/kg', 
		'units' : OrderedDict((('J/kg', {'mult' : 1}), ('kJ/kg', {'mult' : 1e3}),))},
	'SpecificEnthalpy' : {'title' : 'specific enthalpy', 'nominalValue' : 1e6, 'SIUnit' : 'J/kg', 'defDispUnit' : 'kJ/kg', 
		'units' : OrderedDict((('J/kg', {'mult' : 1}), ('kJ/kg', {'mult' : 1e3}),))},
	'SpecificInternalEnergy' : {'title' : 'specific internal energy', 'nominalValue' : 1e6, 'SIUnit' : 'J/kg', 'defDispUnit' : 'kJ/kg', 
		'units' : OrderedDict((('J/kg', {'mult' : 1}), ('kJ/kg', {'mult' : 1e3}),))},
	'SpecificEntropy' : {'title' : 'specific entropy', 'nominalValue' : 1e3, 'SIUnit' : 'J/kg-K', 'defDispUnit' : 'kJ/kg-K',
		'units' : OrderedDict((('J/kg-K', {'mult' : 1}), ('kJ/kg-K', {'mult' : 1e3}),))},
	'SpecificHeatCapacity' : {'title' : 'specific heat capacity', 'nominalValue' : 1e3, 'SIUnit' : 'J/kg-K', 'defDispUnit' : 'kJ/kg-K',
		'units' : OrderedDict((('J/kg-K', {'mult' : 1}), ('kJ/kg-K', {'mult' : 1e3}),))},
	'ThermalConductivity' : {'title' : 'thermal conductivity', 'nominalValue' : 1.0, 'SIUnit' : 'W/m-K', 'defDispUnit' : 'W/m-K',
		'units' : OrderedDict((('W/m-K', {'mult' : 1}),))},
	'DynamicViscosity' : {'title' : 'dynamic viscosity', 'nominalValue' : 1.0, 'SIUnit' : 'Pa-s', 'defDispUnit' : 'Pa-s',
		'units' : OrderedDict((('Pa-s', {'mult' : 1}), ('mPa-s', {'mult' : 1e-3}), ('P', {'mult' : 0.1}), ('cP', {'mult' : 1e-3}),))},
	'VaporQuality' : {'title' : 'vapor quality', 'nominalValue' : 1, 'SIUnit' : '-', 
		'units' : OrderedDict((('-', {'mult' : 1}),))},
	'MassFlowRate' : {'title' : 'mass flow rate', 'nominalValue' : 1, 'SIUnit' : 'kg/s', 
		'units' : OrderedDict((('kg/s', {'mult' : 1}), ('g/s', {'mult' : 1e-3}), ('kg/min', {'mult' : 1./60}), ('g/min', {'mult' : 1e-3/60}), 
			('kg/h', {'mult' : 1/3.6e3}), ('g/h', {'mult' : 1e-3/3.6e3}),))},
	'VolumetricFlowRate' : {'title' : 'volumetric flow rate', 'nominalValue' : 1, 'SIUnit' : 'm**3/s', 
		'units' : OrderedDict((('m**3/s', {'mult' : 1}), ('m**3/h', {'mult' : 1./3.6e3}), ('L/s', {'mult' : 1e-3}),
			('L/min', {'mult' : 1e-3/60}), ('L/h', {'mult' : 1e-3/3.6e3}),))}
}