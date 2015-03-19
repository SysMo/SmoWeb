import numpy as np
from smo.flow import FrictionFlow
try:
	import pylab as plt
except Exception: 
	pass
import scipy.interpolate
import math
from smo.media.CoolProp.CoolProp import FluidState

TOutRec = []

class ComputationModel(object):
	# Method for passing the model values to a computation method 
	# and setting the result values back to the model attributes
	@classmethod
	def setResValues(cls, func, model, fState = None):
		resDict = func(fStateFilm = fState, **model.__dict__)
		for key, value in resDict.iteritems():
			model.__setattr__(key, value)

class PipeFlow(ComputationModel):
	@staticmethod
	def compute(model):
		if (model.computeWithIteration == True):
			PipeFlow.computeWithIteration(model)
		else: 
			PipeFlow.computeWithoutIteration(model)	
	
	@staticmethod
	def computeWithoutIteration(model):
		PipeFlow.setResValues(PipeFlow.computeGeometry, model)
		PipeFlow.setResValues(PipeFlow.computePressureDrop, model)
		PipeFlow.setResValues(PipeFlow.computeHeatExchange, model)
	
	@staticmethod
	def computeWithIteration(model):
		PipeFlow.setResValues(PipeFlow.computeGeometry, model)
		
		#In state
		fStateIn = FluidState(model.fluidName)
		fStateIn.update_Tp(model.inletTemperature, model.inletPressure)
		model.inletEnthalpy = fStateIn.h
		
		# Mean state
		fStateMean = FluidState(model.fluidName)
		outletTemperature_guess = (model.inletTemperature + model.TWall) / 2.
		model.outletTemperature = outletTemperature_guess
		prevOutletTemperature = model.outletTemperature
		
		for i in range(int(model.maxIterations)):
			meanTemperature = (model.inletTemperature + outletTemperature_guess) / 2.
			fStateMean.update_Tp(meanTemperature, model.inletPressure)
			PipeFlow.setResValues(PipeFlow.computePressureDrop, model, fState = fStateMean)
			PipeFlow.setResValues(PipeFlow.computeHeatExchange, model, fState = fStateMean)
			if (abs(prevOutletTemperature - model.outletTemperature) / prevOutletTemperature < model.relativeTolerance):
				break
			if (abs(model.outletTemperature - model.TWall) < 0.01):
				break
			outletTemperature_guess = model.outletTemperature
		
# 		T = np.array(TOutRec)
# 		plt.plot(T)
# 		plt.plot(np.arange(len(T)), model.TWall * np.ones(len(T)))
# 		plt.show()
		
	@staticmethod
	def computeGeometry(internalDiameter, externalDiameter, length, pipeMaterial, **extras):
		if (externalDiameter <= internalDiameter):
			raise ValueError('External diameter value must be bigger than internal diameter value.')
		crossSectionalArea = np.pi / 4 * internalDiameter ** 2
		fluidVolume = crossSectionalArea * length
		internalSurfaceArea = np.pi * internalDiameter * length
		externalSurfaceArea = np.pi * externalDiameter * length
		pipeSolidMass = pipeMaterial['refValues']['density'] \
			* np.pi / 4 * (externalDiameter**2 - internalDiameter**2) * length
		
		return {
				'fluidVolume': fluidVolume, 
				'internalSurfaceArea': internalSurfaceArea,
				'externalSurfaceArea': externalSurfaceArea,
				'crossSectionalArea': crossSectionalArea,
				'pipeSolidMass': pipeSolidMass
				}
	
	@staticmethod		
	def computePressureDrop(internalDiameter, externalDiameter, length, surfaceRoughness, 
						fluidName, inletPressure, inletTemperature, inletMassFlowRate, 
						fStateFilm = None, **extras):
		
		if (fStateFilm is None):
			fStateFilm = FluidState(fluidName)
			fStateFilm.update_Tp(inletTemperature, inletPressure)
		
		inletDensity = fStateFilm.rho
		massFlowRate = inletMassFlowRate
		crossSectionalArea = np.pi / 4 * internalDiameter ** 2
		fluidVolume = crossSectionalArea * length
		fluidMass = fluidVolume * inletDensity
		volumetricFlowRate = massFlowRate / inletDensity	
		flowVelocity = massFlowRate / (inletDensity * crossSectionalArea)
		Re = inletDensity * flowVelocity * internalDiameter / fStateFilm.mu
		zeta = FrictionFlow.ChurchilCorrelation(Re, internalDiameter, surfaceRoughness)
		dragCoefficient = zeta * length / internalDiameter
		pressureDrop = dragCoefficient * inletDensity * flowVelocity * flowVelocity / 2
		outletPressure = inletPressure - pressureDrop
		if (outletPressure <= 0):
			raise ValueError("This mass flow rate cannot be achieved.")	
		
		return {'inletDensity': inletDensity,
				'fluidMass': fluidMass,
				'massFlowRate': massFlowRate,
				'volumetricFlowRate': volumetricFlowRate,
				'flowVelocity': flowVelocity,
				'Re': Re,
				'zeta': zeta,
				'dragCoefficient': dragCoefficient,
				'pressureDrop': pressureDrop,
				'outletPressure': outletPressure
				}
	
	
	# Heat Atlas, p.697, eq. 26, 27
	@staticmethod	
	def computeHeatExchange(internalDiameter, length, TWall, 
						fluidName, inletPressure, inletTemperature, inletMassFlowRate, outletPressure, 
						computeWithIteration, inletEnthalpy = None, outletTemperature = None, fStateFilm = None, **extras):
		
		if (fStateFilm is None):
			fStateFilm = FluidState(fluidName)
			fStateFilm.update_Tp(inletTemperature, inletPressure)
			inletEnthalpy = fStateFilm.h
		
		####
		inletDensity = fStateFilm.rho
		massFlowRate = inletMassFlowRate
		crossSectionalArea = np.pi / 4 * internalDiameter ** 2
		internalSurfaceArea = np.pi * internalDiameter * length
		flowVelocity = massFlowRate / (inletDensity * crossSectionalArea)
		Re = inletDensity * flowVelocity * internalDiameter / fStateFilm.mu
		###
		
		Pr = fStateFilm.Pr
		cond = fStateFilm.cond
		
		# Determining Nusselt number
		if (Re <= 2.3e3):
			# laminar flow
			Nu = 3.66
		elif (Re > 2.3e3 and Re < 1e4):
			# transition	
			interpCoeff = (Re - 2.3e3) / (1e4 - 2.3e3) 
			Nu_low = 3.66
			xi = (1.8 * 4 - 1.5)**(-2)
			Nu_high = ((xi / 8.) * 1e4 * Pr) / (1 + 12.7 * math.sqrt(xi / 8.) * (Pr**(2 / 3.) - 1)) * \
			(1 + (internalDiameter / length)**(2 / 3.))
			Nu = interpCoeff * Nu_high + (1 - interpCoeff) * Nu_low
		elif (Re >= 1e4 and Re <= 1e6):
			# turbulent flow
			xi = (1.8 * math.log(Re, 10) - 1.5)**(-2)
			Nu = ((xi / 8.) * Re * Pr) / (1 + 12.7 * math.sqrt(xi / 8.) * (Pr**(2 / 3.) - 1))
		elif (Re > 1e6):
			raise ValueError("Outside range of validity")
		
		alpha = cond * Nu / internalDiameter
		
		if (computeWithIteration == True):			
			LMTD = - (outletTemperature - inletTemperature) / \
					math.log((TWall - inletTemperature) / \
						(TWall - outletTemperature))
			QDot = alpha * internalSurfaceArea * LMTD
		else:
			QDot = alpha * internalSurfaceArea * (inletTemperature - TWall)
		
		outletEnthalpy = inletEnthalpy - (QDot / massFlowRate)
		
		fStateOut = FluidState(fluidName)
		fStateOut.update_ph(outletPressure, outletEnthalpy)
		prevOutletTemperature = outletTemperature 
		outletTemperature = fStateOut.T
		
		if ((outletTemperature - TWall)*(inletTemperature - TWall) < 0):
			if (computeWithIteration == True):
				outletTemperature = 0.5 * prevOutletTemperature + 0.5 * TWall
			else:
				outletTemperature = TWall
		else:
			if (computeWithIteration == True):
				outletTemperature = 0.9 * prevOutletTemperature + 0.1 * outletTemperature	
			
# 		TOutRec.append(outletTemperature)
# 		print ('-------')
# 		print ('inletTemperature: %e'%inletTemperature)
# 		print ('outletTemperature: %e'%outletTemperature)
# 		print ('TWall: %e'%TWall)
# 		print ('dTOut = %e'%(outletTemperature - TWall))
# 		print ('')
		
		return {'Pr': Pr,
				'Nu': Nu,
				'alpha': alpha,
				'QDot': QDot,
				'outletTemperature': outletTemperature
				}


# Left for testing purposes !!!	
# 	@staticmethod
# 	def computeWithIteration1(model):
# 		### Geometry
# 		if (model.externalDiameter <= model.internalDiameter):
# 			raise ValueError('External diameter value must be bigger than internal diameter value.')
# 		model.crossSectionalArea = np.pi / 4 * model.internalDiameter ** 2
# 		model.fluidVolume = model.crossSectionalArea * model.length
# 		model.internalSurfaceArea = np.pi * model.internalDiameter * model.length
# 		model.externalSurfaceArea = np.pi * model.externalDiameter * model.length
# 		model.pipeSolidMass = model.pipeMaterial['refValues']['density'] \
# 			* np.pi / 4 * (model.externalDiameter**2 - model.internalDiameter**2) * model.length
# 		
# 		### Flow
# 		model.massFlowRate = model.inletMassFlowRate
# 		outletTemperature_guess = (model.inletTemperature + model.TWall) / 2.
# 		fStateIn = FluidState(model.fluidName)
# 		fStateMean = FluidState(model.fluidName)
# 		fStateOut = FluidState(model.fluidName)
# 		fStateIn.update_Tp(model.inletTemperature, model.inletPressure)
# 		model.inletEnthalpy = fStateIn.h
# 		
# 		for i in range(10):
# 			meanTemperature = (model.inletTemperature + outletTemperature_guess) / 2.		
# 			### Flow
# 			fStateMean.update_Tp(meanTemperature, model.inletPressure)
# 			model.inletDensity = fStateMean.rho
# 			model.fluidMass = model.fluidVolume * model.inletDensity
# 			model.volumetricFlowRate = model.massFlowRate / model.inletDensity	
# 			model.flowVelocity = model.massFlowRate / (model.inletDensity * model.crossSectionalArea )
# 			model.Re = model.inletDensity * model.flowVelocity * model.internalDiameter / fStateMean.mu
# 			
# 			### Pressure drop
# 			model.zeta = FrictionFlow.ChurchilCorrelation(model.Re, model.internalDiameter, model.surfaceRoughness)
# 			model.dragCoefficient = model.zeta * model.length / model.internalDiameter
# 			model.pressureDrop = model.dragCoefficient * model.inletDensity * model.flowVelocity * model.flowVelocity / 2
# 			model.outletPressure = model.inletPressure - model.pressureDrop
# 			
# 			### Heat exchange
# 			model.Pr = fStateMean.Pr
# 			model.cond = fStateMean.cond
# 			
# 			# Determining Nusselt number
# 			if (model.Re <= 2.3e3):
# 				# laminar flow
# 				model.Nu = 3.66
# 			elif (model.Re > 2.3e3 and model.Re < 1e4):
# 				# transition	
# 				interpCoeff = (model.Re - 2.3e3) / (1e4 - 2.3e3) 
# 				Nu_low = 3.66
# 				eps = (1.8 * 4 - 1.5)**(-2)
# 				Nu_high = ((eps / 8.) * 1e4 * model.Pr) / (1 + 12.7 * math.sqrt(eps / 8.) * (model.Pr**(2 / 3.) - 1)) * \
# 				(1 + (model.internalDiameter / model.length)**(2 / 3.))
# 				model.Nu = interpCoeff * Nu_high + (1 - interpCoeff) * Nu_low
# 			elif (model.Re >= 1e4 and model.Re <= 1e6):
# 				# turbulent flow
# 				eps = (1.8 * math.log10(model.Re) - 1.5)**(-2)
# 				model.Nu = ((eps / 8.) * model.Re * model.Pr) / (1 + 12.7 * math.sqrt(eps / 8.) * (model.Pr**(2 / 3.) - 1)) * \
# 				(1 + (model.internalDiameter / model.length)**(2 / 3.))
# 			elif (model.Re > 1e6):
# 				raise ValueError("Outside range of validity")
# 			
# 			model.alpha = model.cond * model.Nu / model.internalDiameter
# 			LMTD = - (outletTemperature_guess - model.inletTemperature) / \
# 					math.log((model.TWall - model.inletTemperature) / \
# 						(model.TWall - outletTemperature_guess))
# 			#model.QDot = model.alpha * model.internalSurfaceArea * (meanTemperature - model.TWall)
# 			model.QDot = model.alpha * model.internalSurfaceArea * LMTD
# 			model.outletEnthalpy = model.inletEnthalpy - (model.QDot / model.massFlowRate)
# 			fStateOut.update_ph(model.outletPressure, model.outletEnthalpy)
# 			outletTemperature_guess = fStateOut.T	
# 		model.outletTemperature = outletTemperature_guess