'''
Created on Sep 15, 2014

@author: Atanas Pavlov
'''
from Media import Medium

RegisteredFluids = {}

def getFluid(fluidName):
	if (fluidName in RegisteredFluids.keys()):			
		fluid = RegisteredFluids[fluidName]
	else:
		fluid = Medium.create(Medium.sCompressibleFluidCoolProp,
			 fluidName, len(RegisteredFluids))
		RegisteredFluids[fluidName] = fluid
