from smo.media.CoolProp.CoolProp import Fluid, FluidState
ThermodynamicVariables = {
	'p' : {'label': 'pressure', 'scale': 1e5, 'unit': 'bar'},
	'T' : {'label': 'temperature', 'scale': 1.0, 'unit': 'K'},
	'h' : {'label': 'enthalpy', 'scale': 1e3, 'unit': 'kJ/kg'},
	's' : {'label': 'entropy', 'scale': 1e3, 'unit': 'kJ/kg-K'},
	'w' : {'label': 'work', 'scale': 1e3, 'unit': 'kJ/kg'},
}

class CycleComponent(object):
	def __init__(self):
		self.w = 0
		self.qIn = 0

class CompressorOneStage(CycleComponent):
	def __init__(self, type, eta, fQ):
		self.type = type
		self.eta = eta
		self.fQ = fQ
	
	def compute(self, pOut):
		self.outlet.update_ps(pOut, self.inlet.s)
		wIdeal = self.outlet.h - self.inlet.h
		self.w = wIdeal / self.eta
		self.qIn = - self.fQ * self.w
		delta_h = self.w + self.qIn
		self.outlet.update_ph(pOut, self.inlet.h + delta_h)


class IsobaricHeatExchanger(CycleComponent):
	def compute(self, computeMethod, **kwargs):
		pIn = kwargs.get('pIn', self.inlet.p)
		if (computeMethod == 'eta'):
			self.outlet.update_Tp(kwargs['TExt'], pIn)
			eta = kwargs['eta']
			hOut = (1 - eta) * self.inlet.h + eta * self.outlet.h
			self.outlet.update_ph(pIn, hOut)
		elif (computeMethod == 'dT'):
			self.outlet.update('P', pIn, 'dT', kwargs['dT'])
		elif (computeMethod == 'Q'):
			self.outlet.update_pq(pIn, kwargs['q'])
		elif (computeMethod == 'T'):
			self.outlet.update_Tp(kwargs['T'], pIn)
		elif (computeMethod == 'H'):
			self.outlet.update_ph(pIn, kwargs['h'])
		else:
			raise ValueError('Unknown compute method {}'.format(computeMethod))
		
		self.qIn = self.outlet.h - self.inlet.h

class ThrottleValve(CycleComponent):
	def compute(self, pOut):
		self.outlet.update_ph(pOut, self.inlet.h)


class ThermodynamicCycle(object):
	def __init__(self, fluid, numPoints):
		self.fp = [FluidState(fluid) for i in range(numPoints)]
		self.fluid = Fluid(fluid)
	
class ReverseBraytonCycle1(ThermodynamicCycle):
	def __init__(self, fluid, compressor, condenser, evaporator):
		super(ReverseBraytonCycle1, self).__init__(fluid, 4)
		self.compressor = compressor
		self.compressor.inlet = self.fp[0] 
		self.compressor.outlet = self.fp[1]
		self.condenser = condenser
		self.condenser.inlet = self.fp[1]
		self.condenser.outlet = self.fp[2]
		self.throttleValve = ThrottleValve()
		self.throttleValve.inlet = self.fp[2]
		self.throttleValve.outlet = self.fp[3]
		self.evaporator = evaporator
		self.evaporator.inlet = self.fp[3]
		self.evaporator.outlet = self.fp[0]
		# Add components
		#self.components.append(self.compressor)
		#self.components.append(self.condenser)
		#self.components.append(self.throttleValve)
		#self.components.append(self.evaporator)
	
	def setTCondensation(self, T):
		if (self.fluid.tripple['T'] < T < self.fluid.critical['T']):
			self.TCondensation = T
			sat = self.fluid.saturation_T(T)
			self.pHigh = sat['psatL']
		else:
			raise ValueError('Condensation temperature ({} K) must be between {} K and {} K'.format(T, self.fluid.tripple['T'], self.fluid.critical['T']))

	def setTEvaporation(self, T):
		if (self.fluid.tripple['T'] < T < self.fluid.critical['T']):
			self.TEvaporation = T
			sat = self.fluid.saturation_T(T)
			self.pLow = sat['psatL']
		else:
			raise ValueError('Evaporation temperature ({} K) must be between {} K and {} K'.format(T, self.fluid.tripple['T'], self.fluid.critical['T']))

	def setPLow(self, p):
		if (self.fluid.tripple['p'] < p < self.fluid.critical['p']):
			self.pLow = p
			sat = self.fluid.saturation_p(p)
			self.TEvaporation = sat['TsatL']
		else:
			raise ValueError('PLow  ({} bar) must be between {} bar and {} bar'.format(p/1e5, self.fluid.tripple['p']/1e5, self.fluid.critical['p']/1e5))

	def setPHigh(self, p):
		if (self.fluid.tripple['p'] < p < self.fluid.critical['p']):
			self.pHigh = p
			sat = self.fluid.saturation_p(p)
			self.TCondensation = sat['TsatL']
		else:
			raise ValueError('PHigh  ({} bar) must be between {} bar and {} bar'.format(p/1e5, self.fluid.tripple['p']/1e5, self.fluid.critical['p']/1e5))
	
# class IsentropicProcess(object):
# 	def __init__(self, fluidName):
# 		self.fluidName = fluidName
# 		self.fluid = Fluid(fluidName)
# 		self.initialState = FluidState(self.fluidName)
# 		
# 	def computeCompression(self, pValues, eta = 1.0):
# 		self.processPoints = []
# 		for p in pValues:
# 			finalState = FluidState(self.fluidName)
# 			finalState.update_ps(p, self.initialState.s)		
# 			idealWork = finalState.h - self.initialState.h
# 			realWork = idealWork / eta
# 			finalState.update_ph(p, self.initialState.h + realWork)
# 			self.processPoints.append(finalState)
# 			
# 	
# 	def getProcessValues(self, variable = 'p'):
# 		values = [f.__getattribute__(variable) for f in self.processPoints]
# 		return np.array(values)
# 		
# 	def plotProcess(self, xAxis = 'p', yAxis = 'T', ax = None, label = None):
# 		TV = ThermodynamicVariables
# 		xValues = self.getProcessValues(xAxis)
# 		if (yAxis == 'w'):
# 			yValues = self.getProcessValues('h') - self.initialState.h			
# 		else:	
# 			yValues = self.getProcessValues(yAxis)
# 		if (ax is None):
# 			fig = plt.figure()
# 			ax = fig.add_subplot(1, 1, 1)
# 		ax.plot(xValues / TV[xAxis]['scale'], yValues / TV[yAxis]['scale'], label = label)
# 		ax.set_xlabel('%s [%s]' % (TV[xAxis]['label'], TV[xAxis]['unit']))
# 		ax.set_ylabel('%s [%s]' % (TV[yAxis]['label'], TV[yAxis]['unit']))
# 		ax.grid(True)
# 		ax.legend(loc = 'upper left')
# 		return ax
# 		
# if __name__ == '__main__':
# 	p = IsentropicProcess('ParaHydrogen')
# 	p.initialState.update_pq(2.6e5, 0.0)
# 	pFinal = np.arange(50e5, 800e5, 10e5, dtype = np.float)
# 	p.computeCompression(pFinal, 1.0)
# 	ax = p.plotProcess('p', 'T', label = 'eta = 1.0')
# 	p.computeCompression(pFinal, 0.9)
# 	p.plotProcess('p', 'T', ax, label = 'eta = 0.9')
# 	p.computeCompression(pFinal, 0.8)
# 	p.plotProcess('p', 'T', ax, label = 'eta = 0.8')
# 	plt.show()
# 	
	