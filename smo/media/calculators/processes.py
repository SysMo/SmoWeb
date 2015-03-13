from smo.media.CoolProp.CoolProp import Fluid, FluidState
import numpy as np
import pylab as plt

ThermodynamicVariables = {
	'p' : {'label': 'pressure', 'scale': 1e5, 'unit': 'bar'},
	'T' : {'label': 'temperature', 'scale': 1.0, 'unit': 'K'},
	'h' : {'label': 'enthalpy', 'scale': 1e3, 'unit': 'kJ/kg'},
	's' : {'label': 'entropy', 'scale': 1e3, 'unit': 'kJ/kg-K'},
	'w' : {'label': 'work', 'scale': 1e3, 'unit': 'kJ/kg'},
}

class Compressor(object):
	def __init__(self, type, eta, fQ):
		self.type = type
		self.eta = eta
		self.fQ = fQ
	
	def compute(self):
		pass

class ThermodynamicCycle(object):
	pass

class ReverseBraytonCycle(ThermodynamicCycle):
	def __init__(self, fluidName):
		self.fluid = Fluid(fluidName)
		self.p1 = FluidState(self.fluid)
		self.p2 = FluidState(self.fluid)
		self.p3 = FluidState(self.fluid)
		self.p4 = FluidState(self.fluid)
# 		c1 = Compressor()
# 		c2 = Condensor()
# 		c3 = ThrottleValve()
# 		c4 = Evaporator()
		


class IsentropicProcess(object):
	def __init__(self, fluidName):
		self.fluidName = fluidName
		self.fluid = Fluid(fluidName)
		self.initialState = FluidState(self.fluidName)
		
	def computeCompression(self, pValues, eta = 1.0):
		self.processPoints = []
		for p in pValues:
			finalState = FluidState(self.fluidName)
			finalState.update_ps(p, self.initialState.s)		
			idealWork = finalState.h - self.initialState.h
			realWork = idealWork / eta
			finalState.update_ph(p, self.initialState.h + realWork)
			self.processPoints.append(finalState)
			
	
	def getProcessValues(self, variable = 'p'):
		values = [f.__getattribute__(variable) for f in self.processPoints]
		return np.array(values)
		
	def plotProcess(self, xAxis = 'p', yAxis = 'T', ax = None, label = None):
		TV = ThermodynamicVariables
		xValues = self.getProcessValues(xAxis)
		if (yAxis == 'w'):
			yValues = self.getProcessValues('h') - self.initialState.h			
		else:	
			yValues = self.getProcessValues(yAxis)
		if (ax is None):
			fig = plt.figure()
			ax = fig.add_subplot(1, 1, 1)
		ax.plot(xValues / TV[xAxis]['scale'], yValues / TV[yAxis]['scale'], label = label)
		ax.set_xlabel('%s [%s]' % (TV[xAxis]['label'], TV[xAxis]['unit']))
		ax.set_ylabel('%s [%s]' % (TV[yAxis]['label'], TV[yAxis]['unit']))
		ax.grid(True)
		ax.legend(loc = 'upper left')
		return ax
		
if __name__ == '__main__':
	p = IsentropicProcess('ParaHydrogen')
	p.initialState.update_pq(2.6e5, 0.0)
	pFinal = np.arange(50e5, 800e5, 10e5, dtype = np.float)
	p.computeCompression(pFinal, 1.0)
	ax = p.plotProcess('p', 'T', label = 'eta = 1.0')
	p.computeCompression(pFinal, 0.9)
	p.plotProcess('p', 'T', ax, label = 'eta = 0.9')
	p.computeCompression(pFinal, 0.8)
	p.plotProcess('p', 'T', ax, label = 'eta = 0.8')
	plt.show()
	
	