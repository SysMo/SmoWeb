import numpy

from collections import OrderedDict
Quantities = {
	'Float' : {'title' : 'dimensionless quantity', 'nominalValue' : 1.0, 'SIUnit' : '-', 
			'units' : OrderedDict((('-', {'mult' : 1}),))},
	'Dimensionless' : {'title' : 'dimensionless quantity', 'nominalValue' : 1.0, 'SIUnit' : '-', 
			'units' : OrderedDict((('-', {'mult' : 1}),))},
			
	'Efficiency' : {'title' : 'efficiency', 'minValue' : 0.0, 'maxValue' : 1.0, 'nominalValue' : 1.0, 'SIUnit' : '-', 
			'units' : OrderedDict((('-', {'mult' : 1}), ('%', {'mult' : 1e-2}),))},
	'Fraction' : {'title' : 'fraction', 'minValue' : 0.0, 'maxValue' : 1.0, 'nominalValue' : 1.0, 'SIUnit' : '-', 
			'units' : OrderedDict((('-', {'mult' : 1}), ('%', {'mult' : 1e-2}), (u'\u2030', {'mult' : 1e-3}), ('ppm', {'mult' : 1e-6}), ('ppb', {'mult' : 1e-9}),))},
	
	'Length' : {'title' : 'length', 'nominalValue' : 1.0, 'SIUnit' : 'm',
		'units' : OrderedDict((('nm', {'mult' : 1e-9}), ('um', {'mult' : 1e-6}), ('mm', {'mult' : 1e-3}), ('cm', {'mult' : 1e-2}), ('m', {'mult' : 1}), 
			('km', {'mult' : 1e3}), ('in', {'mult' : 2.54e-2}), ('ft', {'mult' : 3.048e-1}), ('yd', {'mult' : 0.9144}), ('mi', {'mult' : 1609.344}),))},
	
	'Area' : {'title' : 'area', 'nominalValue' : 1.0, 'SIUnit' : 'm**2', 'minValue' : 0.0, 
		'units' : {'m**2' : {'mult' : 1}, 'cm**2' : {'mult' : 1e-4}, 'mm**2' : {'mult' : 1e-6}}},
	'Volume' : {'title' : 'volume', 'nominalValue' : 1.0, 'SIUnit' : 'm**3', 'minValue' : 0,
		'units' : OrderedDict((('m**3', {'mult' : 1}), ('L', {'mult' : 1e-3}), ('cm**3', {'mult' : 1e-6}), ('mm**3', {'mult' : 1e-9}),))},
	'Time' : {'title' : 'time', 'nominalValue' : 1.0, 'SIUnit' : 's', 
		'units' : OrderedDict((('s', {'mult' : 1}), ('ms', {'mult' : 1e-3}), ('us', {'mult' : 1e-6}), ('min', {'mult' : 60}), ('h', {'mult' : 3600}), ('day', {'mult' : 8.64e4}), ('year', {'mult' : 3.15576e7}),))},
	'Frequency' : {'title' : 'frequency', 'nominalValue' : 1.0, 'SIUnit' : '1/s',
		'units' : OrderedDict((('1/s', {'mult' : 1}), ('1/min', {'mult' : 1./60}), ('1/h', {'mult' : 1./3600}), ('1/day', {'mult' : 1./8.64e4}),))},
	'TimeRate' : {'title' : 'time rate', 'nominalValue' : 1.0, 'SIUnit' : '1/s',
		'units' : OrderedDict((('1/s', {'mult' : 1}), ('1/min', {'mult' : 1./60}), ('1/h', {'mult' : 1./3600}), ('1/day', {'mult' : 1./8.64e4}),))},
	'AngularVelocity' : {'title' : 'angular velocity', 'nominalValue' : 1.0, 'SIUnit' : 'rev/s',
		'units' : OrderedDict((('rev/s', {'mult' : 1}), ('rev/min', {'mult' : 1./60}), ('rev/h', {'mult' : 1./3600}), ('rad/s', {'mult' : 1./(2*numpy.pi)}),))},
	'Angle' : {'title' : 'angle', 'nominalValue' : numpy.pi/4, 'SIUnit' : 'rad', 
		'units' : OrderedDict((('rad', {'mult' : 1}), ('deg', {'mult' : numpy.pi/180})))},
	'Force' : {'title' : 'force', 'nominalValue' : 1.0, 'SIUnit' : 'N', 
		'units' : OrderedDict((('N', {'mult' : 1}), ('kN', {'mult' : 1e3}), ('MN', {'mult' : 1e6}), ('lb', {'mult' : 4.44822162825}),))},
	'Weight' : {'title' : 'weight', 'nominalValue' : 1.0, 'SIUnit' : 'N', 
		'units' : OrderedDict((('N', {'mult' : 1}), ('kN', {'mult' : 1e3}), ('MN', {'mult' : 1e6}), ('kgf', {'mult' : 9.80665}), ('gf', {'mult' : 9.80665e-3}), ('tf', {'mult' : 9.80665e+3}), ('lb', {'mult' : 4.44822162825}), ('oz', {'mult' : 0.278013851766}),))},
	'Velocity' : {'title' : 'velocity', 'nominalValue' : 1.0, 'SIUnit' : 'm/s', 
			'units' : OrderedDict((('m/s', {'mult' : 1}), ('km/h', {'mult' : 1/3.6}), ('km/s', {'mult' : 1e3}), ('mm/s', {'mult' : 1e-3}),))},
	'Mass' : {'title' : 'mass', 'nominalValue' : 1.0, 'SIUnit' : 'kg', 'minValue' : 0.0,
		'units' : OrderedDict((('kg', {'mult' : 1}), ('g', {'mult' : 1e-3}), ('ton', {'mult' : 1e3}),))},
	'MolarMass' : {'title' : 'molar mass', 'nominalValue' : 1e-3, 'SIUnit' : 'kg/mol', 'defDispUnit' : 'g/mol',
		'units' : OrderedDict((('kg/mol', {'mult' : 1}), ('g/mol', {'mult' : 1e-3}),))},
	'Energy' : {'title' : 'energy', 'nominalValue' : 1.0, 'SIUnit' : 'J', 'defDispUnit' : 'kJ',
		'units' : OrderedDict((('J', {'mult' : 1}), ('kJ', {'mult' : 1e3}), ('MJ', {'mult' : 1e6}), ('GJ', {'mult' : 1e9}), ('Cal', {'mult' : 4.184}), ('kCal', {'mult' : 4.184e3}),
		('Wh', {'mult' : 3.6e3}),  ('kWh', {'mult' : 3.6e6}),  ('MWh', {'mult' : 3.6e9}), ('BTU', {'mult' : 1055}), ('eV', {'mult' : 1.60217657e-19}),))},
	'Power' : {'title' : 'power', 'nominalValue' : 1e3, 'SIUnit' : 'W', 'defDispUnit' : 'kW',
		'units' : OrderedDict((('W', {'mult' : 1}), ('kW', {'mult' : 1e3}), ('MW', {'mult' : 1e6}), ('GW', {'mult' : 1e9}),
		('mW', {'mult' : 1e-3}),  ('uW', {'mult' : 1e-6}),  ('hp', {'mult' : 746.0}), ('BTU/h', {'mult' : 0.293}),))},
	'Pressure' : {'title' : 'pressure', 'nominalValue' : 1e5, 'SIUnit' : 'Pa', 'defDispUnit' : 'bar', 'minValue' : 0.0, 'maxValue' : 1.e12,
		'units' : OrderedDict((('Pa', {'mult' : 1}), ('hPa', {'mult' : 1e2}), ('kPa', {'mult' : 1e3}), ('MPa', {'mult' : 1e6}), ('GPa', {'mult' : 1e9}), 
			('mbar', {'mult' : 1e2}), ('bar', {'mult' : 1e5}), ('psi', {'mult' : 6.89475e3}), ('ksi', {'mult' : 6.89475e6}), ('kN/m**2', {'mult' : 1e3}), ('kN/cm**2', {'mult' : 1e7}), ('kN/mm**2', {'mult' : 1e9}),))},
	'Temperature' : {'title' : 'temperature', 'nominalValue' : 288, 'SIUnit' : 'K', 'minValue' : 0.0, 'maxValue' : 1.e9, 
		'units' : OrderedDict((('K', {'mult' : 1}), ('degC', {'mult' : 1, 'offset' : 273.15}), 
							('degF', {'mult' : 5./9, 'offset' : 255.372222222222}), ('degR', {'mult' : 5./9})))},
	'TemperatureDifference' : {'title' : 'temperature difference', 'nominalValue' : 1.0, 'SIUnit' : 'K', 
		'units' : OrderedDict((('K', {'mult' : 1}), ('degC', {'mult' : 1}), ('degF', {'mult' : 5./9}), ('degR', {'mult' : 5./9})))},
	'Density' : {'title' : 'density', 'nominalValue' : 1.0, 'SIUnit' : 'kg/m**3', 
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
			
	# Thermal
	'HeatFlowRate' : {'title' : 'heat flow rate', 'nominalValue' : 1e3, 'SIUnit' : 'W', 'defDispUnit' : 'kW',
		'units' : OrderedDict((('W', {'mult' : 1}), ('kW', {'mult' : 1e3}), ('MW', {'mult' : 1e6}), ('GW', {'mult' : 1e9}),
		('mW', {'mult' : 1e-3}),  ('uW', {'mult' : 1e-6}),  ('hp', {'mult' : 746.0}), ('BTU/h', {'mult' : 0.293}),))},
	'HeatFluxDensity' : {'title' : 'heat flux density', 'nominalValue' : 1.0, 'SIUnit' : 'W/m**2', 'defDispUnit' : 'W/m**2',
		'units' : OrderedDict((('W/m**2', {'mult' : 1}), ('kW/m**2', {'mult' : 1e3})))},
	'LinearHeatFluxDensity' : {'title' : 'linear heat flux density', 'nominalValue' : 1.0, 'SIUnit' : 'W/m', 'defDispUnit' : 'W/m',
		'units' : OrderedDict((('W/m', {'mult' : 1}), ('kW/m', {'mult' : 1e3})))},
	'ThermalConductivity' : {'title' : 'thermal conductivity', 'nominalValue' : 1.0, 'SIUnit' : 'W/m-K', 'defDispUnit' : 'W/m-K',
		'units' : OrderedDict((('W/m-K', {'mult' : 1}), ('W/cm-K', {'mult' : 1e2}), ('W/mm-K', {'mult' : 1e3})))},
	'ThermalExpansionCoefficient' : {'title' : 'thermal expansion coefficient', 'nominalValue' : 1.0, 'SIUnit' : '1/K', 'defDispUnit' : '1/K',
		'units' : OrderedDict((('1/K', {'mult' : 1}), ('1/mK', {'mult' : 1e-3}), ('1/degC', {'mult' : 1}), ('1/degF', {'mult' : 9./5})))},
	'HeatTransferCoefficient' : {'title' : 'heat transfer coefficient', 'nominalValue' : 1.0, 'SIUnit' : 'W/m**2-K', 'defDispUnit' : 'W/m**2-K',
		'units' : OrderedDict((('W/m**2-K', {'mult' : 1}), ('kW/m**2-K', {'mult' : 1e3}), ('W/cm**2-K', {'mult' : 1e4})))},
	'ThermalResistance' : {'title' : 'thermal resistance', 'nominalValue' : 1.0, 'SIUnit' : 'K/W', 'defDispUnit' : 'K/W',
		'units' : OrderedDict((('K/W', {'mult' : 1}), ('K/kW', {'mult' : 1e-3})))},
	'ThermalConductance' : {'title' : 'thermal conductance', 'nominalValue' : 1.0, 'SIUnit' : 'W/K', 'defDispUnit' : 'W/K',
		'units' : OrderedDict((('W/K', {'mult' : 1}), ('kW/K', {'mult' : 1e3})))},
			
	# Electrical
	'ElectricalConductivity' : {'title' : 'electrical conductivity', 'nominalValue' : 1.0, 'SIUnit' : 'S/m', 'defDispUnit' : 'S/m',
		'units' : OrderedDict((('S/m', {'mult' : 1}), ('S/cm', {'mult' : 1e2}), ('S/mm', {'mult' : 1e3})))},
	'ElectricalResistivity' : {'title' : 'electrical resistivity', 'nominalValue' : 1.0, 'SIUnit' : 'Ohm-m', 'defDispUnit' : 'Ohm-m',
		'units' : OrderedDict((('Ohm-m', {'mult' : 1}), ('Ohm-cm', {'mult' : 1e-2}), ('Ohm-mm', {'mult' : 1e-3})))},			
	'ElectricalResistance' : {'title' : 'electrical resistance', 'nominalValue' : 1.0, 'SIUnit' : 'Ohm', 'defDispUnit' : 'Ohm',
		'units' : OrderedDict((('mOhm', {'mult' : 1e-3}), ('Ohm', {'mult' : 1}), ('kOhm', {'mult' : 1e3}),
			('MOhm', {'mult' : 1e6}), ('GOhm', {'mult' : 1e9})))},
	'ElectricalCurrent' : {'title' : 'electrical current', 'nominalValue' : 1.0, 'SIUnit' : 'A', 'defDispUnit' : 'A',
		'units' : OrderedDict((('nA', {'mult' : 1e-9}), ('uA', {'mult' : 1e-6}), ('mA', {'mult' : 1e-3}), 
			('A', {'mult' : 1}), ('kA', {'mult' : 1e3})))},			
	
	# Flow	
	'DynamicViscosity' : {'title' : 'dynamic viscosity', 'nominalValue' : 1.0, 'SIUnit' : 'Pa-s', 'defDispUnit' : 'Pa-s',
		'units' : OrderedDict((('Pa-s', {'mult' : 1}), ('mPa-s', {'mult' : 1e-3}), ('P', {'mult' : 0.1}), ('cP', {'mult' : 1e-3}),))},
	'VaporQuality' : {'title' : 'vapor quality', 'nominalValue' : 1.0, 'SIUnit' : '-', 
		'units' : OrderedDict((('-', {'mult' : 1}),))},
	'MassFlowRate' : {'title' : 'mass flow rate', 'nominalValue' : 1.0, 'SIUnit' : 'kg/s', 
		'units' : OrderedDict((('kg/s', {'mult' : 1}), ('g/s', {'mult' : 1e-3}), ('kg/min', {'mult' : 1./60}), ('g/min', {'mult' : 1e-3/60}), 
			('kg/h', {'mult' : 1/3.6e3}), ('g/h', {'mult' : 1e-3/3.6e3}),))},
	'VolumetricFlowRate' : {'title' : 'volumetric flow rate', 'nominalValue' : 1.0, 'SIUnit' : 'm**3/s', 
		'units' : OrderedDict((('m**3/s', {'mult' : 1}), ('m**3/h', {'mult' : 1./3.6e3}), ('L/s', {'mult' : 1e-3}),
			('L/min', {'mult' : 1e-3/60}), ('L/h', {'mult' : 1e-3/3.6e3}),))},
			
	# Bio-units
	'Bio_Time' : {'title' : 'bio: time', 'nominalValue' : 1.0, 'SIUnit' : 'day', 
		'units' : OrderedDict((('s', {'mult' : 1/86400.}), ('min', {'mult' : 1/1440.}), ('h', {'mult' : 1/24.}), ('day', {'mult' : 1.0}), ('year', {'mult' : 365.}),))},
	'Bio_TimeRate' : {'title' : 'bio: time rate', 'nominalValue' : 1.0, 'SIUnit' : '1/day',
		'units' : OrderedDict((('1/s', {'mult' : 86400.}), ('1/min', {'mult' : 1440.}), ('1/h', {'mult' : 24.}), ('1/day', {'mult' : 1.0}),))},
	'Bio_Mass' : {'title' : 'bio: mass', 'nominalValue' : 1.0, 'SIUnit' : 'kgCOD', 'minValue' : 0.0,
		'units' : OrderedDict((('kgCOD', {'mult' : 1}), ('gCOD', {'mult' : 1e-3}), ('tonCOD', {'mult' : 1e3}),))},
	'Bio_MassConcentration' : {'title' : 'bio: mass concentration', 'nominalValue' : 1.0, 'minValue' : 0.0, 'SIUnit' : 'kg/m**3', 
		'units' : OrderedDict((('kg/m**3', {'mult' : 1}), ('g/L', {'mult' : 1}), ('g/cm**3', {'mult' : 1e3}),))},
	'Bio_CODConcentration' : {'title' : 'bio: COD concentration', 'nominalValue' : 1.0, 'minValue' : 0.0, 'SIUnit' : 'kgCOD/m**3', 
		'units' : OrderedDict((('kgCOD/m**3', {'mult' : 1}), ('gCOD/L', {'mult' : 1}), ('gCOD/cm**3', {'mult' : 1e3}),))},
	'Bio_MolarConcentration' : {'title' : 'bio: molar concentration', 'nominalValue' : 1.0, 'minValue' : 0.0, 'SIUnit' : 'kmol/m**3', 
		'units' : OrderedDict((('kmol/m**3', {'mult' : 1}), ('mol/m**3', {'mult' : 1./1e3}), ('mol/L', {'mult' : 1}), ('M', {'mult' : 1}), ('mol/cm**3', {'mult' : 1e3}),))},
	'Bio_VolumetricFlowRate' : {'title' : 'bio: volumetric flow rate', 'nominalValue' : 1.0, 'SIUnit' : 'm**3/day', 
		'units' : OrderedDict((('m**3/s', {'mult' : 86400.}), ('m**3/min', {'mult' : 1440.}), ('m**3/h', {'mult' : 24.}), ('m**3/day', {'mult' : 1.0}),
							   ('L/s', {'mult' : 1e-3*86400.}), ('L/min', {'mult' : 1e-3*1440.}), ('L/h', {'mult' : 1e-3*24.}), ('L/day', {'mult' : 1e-3*1.0}),))},
	
	'Bio_MassConcentrationFlowRate' : {'title' : 'bio: mass concentration flow rate', 'nominalValue' : 1.0, 'minValue' : 0.0, 'SIUnit' : 'kg/m**3/day', 
		'units' : OrderedDict((
			('kg/m**3/day', {'mult' : 1}), ('g/L/day', {'mult' : 1}), ('g/cm**3/day', {'mult' : 1e3}), 
			('kg/m**3/h', {'mult' : 1*24.}), ('g/L/h', {'mult' : 1*24.}), ('g/cm**3/h', {'mult' : 1e3*24.}),
	))},
				
	'Bio_CODConcentrationFlowRate' : {'title' : 'bio: COD concentration flow rate', 'nominalValue' : 1.0, 'minValue' : 0.0, 'SIUnit' : 'kgCOD/m**3/day', 
		'units' : OrderedDict((
			('kgCOD/m**3/day', {'mult' : 1}), ('gCOD/L/day', {'mult' : 1}), ('gCOD/cm**3/day', {'mult' : 1e3}), 
			('kgCOD/m**3/h', {'mult' : 1*24.}), ('gCOD/L/h', {'mult' : 1*24.}), ('gCOD/cm**3/h', {'mult' : 1e3*24.}),
	))},
}


def convertUnit(data, quantity, fromUnit, toUnit):
		if (fromUnit == toUnit):
			return data
		quantityUnits = Quantities[quantity]['units']
		if (fromUnit not in quantityUnits):
			raise ValueError('Incorrect value {} for parameter "fromUnit"'.format(fromUnit))
		if (toUnit not in quantityUnits):
			raise ValueError('Incorrect value {} for parameter "toUnit"'.format(toUnit))
		fromUnitDef = quantityUnits[fromUnit]
		toUnitDef = quantityUnits[toUnit]
		inUnitOffset = fromUnitDef['offset'] if 'offset' in fromUnitDef else 0
		outUnitOffset = toUnitDef['offset'] if 'offset' in toUnitDef else 0
		data *= fromUnitDef['mult']
		data += inUnitOffset - outUnitOffset
		data /= toUnitDef['mult']
		return data
