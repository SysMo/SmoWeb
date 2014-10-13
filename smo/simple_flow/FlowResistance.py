import numpy as np
import pylab as plt
import scipy.interpolate
from smo.smoflow3d import getFluid
from smo.smoflow3d.Media import MediumState

class Pipe(object):
	def __init__(self, internalDiameter, length, surfaceRoughness = 25e-6):
		self.internalDiameter = internalDiameter
		self.length = length
		self.surfaceRoughness = surfaceRoughness
		self.crossSectionalArea = np.pi / 4 * internalDiameter ** 2
		
	def setUpstreamState(self, pressure, temperature):
		fluidState = MediumState(getFluid('parahydrogen'))
		fluidState.update_Tp(temperature, pressure)

	
	def computePressureDrop(self, upstreamState, mDot):		
		self.v = mDot / (upstreamState.rho() * self.crossSectionalArea )
		self.Re = upstreamState.rho() * self.v * self.crossSectionalArea / upstreamState.mu()
		self.zeta = Pipe.ChurchilCorrelation(self.Re, self.internalDiameter, self.surfaceRoughness)
		self.pressureDrop = self.zeta * self.length / self.internalDiameter * upstreamState.rho() * self.v * self.v / 2
		return self.pressureDrop
		

	@staticmethod
	def ChurchilCorrelation(Re, d, epsilon):
		theta1 = np.power(2.457 * np.log(np.power(7.0 / Re, 0.9) + 0.27 * epsilon / d), 16)
		theta2 = np.power(37530.0 / Re, 16)
		zeta = 8 * np.power(np.power((8.0 / Re), 12) + 1 / np.power((theta1 + theta2), 1.5) , 1./12)
		return zeta

	@staticmethod
	def testChurchilCorrelation():
		Re = np.logspace(2, 6, 1000, base = 10.0)
		d = 5e-3
		epsilon = 25e-7
		zeta = 0 * Re
		for i in range(len(Re)):
			zeta[i] = Pipe.ChurchilCorrelation(Re[i], d, epsilon)
		plt.loglog(Re, zeta)
		plt.show()
		
		
class Orifice(object):
	def __init__(self, diameter, cq):
		self.diameter = diameter
		self.cq = cq
	
	def computeMassFlowRate(self):
		gamma = 1.33
		pUp = 300e5
		pDown = np.linspace(100e5, 299.9e5, 1000)
		ratio = pDown/pUp
		delta = 1 - ratio
		dp = pUp - pDown
		R_g = 1
		crit_ratio = np.power(2/(gamma + 1), gamma / (gamma - 1))
		crit_delta = 1 - crit_ratio
		crit_dp = pUp * crit_delta
		print ('crit. ratio = {0}'.format(crit_ratio))
		cm = np.sqrt(2 * gamma / (R_g * (gamma - 1))) * np.sqrt(np.power(ratio, 2 / gamma) - np.power(ratio, (gamma + 1) / gamma))
		cm_crit = np.sqrt(2 * gamma / (R_g * (gamma + 1))) * np.power(2 / (gamma + 1), 1 / (gamma - 1)) * (1 + 0 * cm)
		cm_approx = np.sqrt(1 - np.power(1 - delta/crit_delta, 2)) * cm_crit
		plt.plot(ratio, cm, 'r')
		plt.plot(ratio, cm_crit, 'm')
		plt.plot(ratio, cm_approx, 'g')
		plt.plot([crit_ratio, crit_ratio], [0, np.max(cm) * 1.1], 'b')
		plt.show()
	
	@staticmethod
	def test():
		orifice = Orifice(3e-3, 1.0)
		orifice.computeMassFlowRate()

class Elbow(object):
	#r_d_90 = np.array([1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20])
	#C_d_90 = np.array([20, 14, 12, 12, 14, 17, 24, 30, 34, 38, 42, 50])
	#interp90 = scipy.interpolate.interp1d(r_d_90, C_d_90)
	AInterp = scipy.interpolate.interp1d(
			np.array([0, 20, 30, 45, 60, 75, 90, 110, 130, 150, 180]),
			np.array([0, 0.31, 0.45, 0.60, 0.78, 0.90, 1.0, 1.13, 1.20, 1.28, 1.40])
	)
	BInterp = scipy.interpolate.interp1d(
			np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.25, 1.5, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50]),
			np.array([1.18, 0.77, 0.51, 0.37, 0.28, 0.21, 0.19, 0.17, 0.15, 0.11, 0.09, 0.07, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03])
	)	

	def __init__(self, internalDiameter, bendRadius, bendAngleDeg, surfaceRoughness = 0.025):
		self.internalDiameter = internalDiameter
		self.bendRadius = bendRadius
		self.surfaceRoughness = surfaceRoughness
		self.crossSectionalArea = np.pi / 4 * self.internalDiameter**2
		
		
		self.turbFrictionFactor = 0.25 / (np.log10(self.surfaceRoughness / self.internalDiameter / 3.7)**2)
		self.r_to_d = self.bendRadius / self.internalDiameter
		
		self.dragCoefficient90 = Elbow.interp90(self.r_to_d) * self.turbFrictionFactor
		
		print self.dragCoefficient90
		
		self.bendAngleDeg = bendAngleDeg
		self.dragCoefficient = (self.bendAngleDeg / 90 - 1) \
				* (0.25 * np.pi * self.r_to_d * self.turbFrictionFactor + 0.5 * self.dragCoefficient90) \
				+ self.dragCoefficient90

		print self.dragCoefficient
		
	def computePressureDrop(self, mDot, rho):
		self.flowVelocity = mDot / rho / self.crossSectionalArea
	
	@staticmethod	
	def test():
		#a = Elbow(internalDiameter = 5.08e-2, bendRadius = 81.28e-2, bendAngleDeg = 30, surfaceRoughness = 0.00005)
		b = Elbow(internalDiameter = 20e-3, bendRadius = 200e-3, bendAngleDeg = 90, surfaceRoughness = 70e-6)

		
if __name__ == '__main__':
	Pipe.testChurchilCorrelation()
	#Orifice.test()
	#Elbow.test()