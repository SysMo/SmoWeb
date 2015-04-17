'''
Created on Apr 14, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import FrictionHeatExchangeCorrelations as CR
from smo.media.CoolProp.CoolProp import FluidState
import numpy as np
import math as m
import pylab as plt

class FluidChannelSection(object):
	def __init__(self, xStart, xEnd, fluid = None):
		self.xStart = xStart
		self.xEnd = xEnd
		self.xMid = (xStart + xEnd) / 2
		self.L = self.xEnd - self.xStart
		if (fluid is not None):
			self.setFluid(fluid)
		
	def setAnnularGeometry(self, dIn, dOut):
		self.flowArea = m.pi / 4 * (dOut**2 - dIn**2)
		self.charLength = dOut - dIn
		self.extWallArea = m.pi * dOut * self.L
		self.NusseltCorrelation = CR.Nusselt_StraightPipe
		epsilon = 0.025
		self.frictionCorrelation = lambda Re: CR.ChurchilCorrelation(Re, dOut - dIn, epsilon)
		self.flowFactor = self.L / self.charLength
		def plotGeometry(patches, dy = 0, dx = 0):
			from matplotlib.patches import Rectangle
			p1 = Rectangle(xy = (self.xStart + dx, dy - dOut / 2), width = self.L, height = dOut, color = '0.3')
			p2 = Rectangle(xy = (self.xStart + dx, dy - dIn / 2), width = self.L, height = dIn, color = 'w')
			patches.append(p1)
			patches.append(p2)
		def plotTemperature(patches, colors, dy = 0, dx = 0):
			self.plotGeometry(patches, dy, dx)
			colors.append(np.NaN)
			colors.append(self.fState.T)
		self.plotGeometry = plotGeometry
		self.plotTemperature = plotTemperature
		
	def setHelicalGeometry_RectChannel(self, axialWidth, radialHeight, Dw, pitch):
		self.flowArea = axialWidth * radialHeight
		self.charLength = 2 * self.flowArea / (axialWidth + radialHeight)
		#self.extWallArea =  (self.L / pitch) * m.pi * (Dw - radialHeight) * axialWidth
		self.extWallArea = m.pi * self.L * (Dw - radialHeight)
		d_D = self.charLength / Dw
		self.NusseltCorrelation = lambda Re, Pr: CR.Nusselt_HelicalChannel(Re, Pr, d_D)
		self.frictionCorrelation = lambda Re: CR.frictionFactor_HelicalChannel(Re, d_D)
		self.flowFactor = (self.L / pitch) * m.pi * Dw / self.charLength
		
	def computeConvectionCoefficient(self):
		if (self.mDot > 1e-12):
			self.vFlow = self.mDot / self.fState.rho / self.flowArea
			self.Re = self.fState.rho * self.vFlow * self.charLength / self.fState.mu
			self.Pr = self.fState.Pr
			self.Nu = self.NusseltCorrelation(self.Re, self.Pr)
			self.hConv = self.Nu * self.fState.cond / self.charLength
		else:
			self.vFlow = 0
			self.Re = 0
			self.Pr = 0
			self.Nu = 0
			self.hConv = 0			
	
	def computePressureDrop(self):
		if (self.mDot > 1e-12):
			self.vFlow = self.mDot / self.fState.rho / self.flowArea
			self.Re = self.fState.rho * self.vFlow * self.charLength / self.fState.mu
			self.zeta = self.frictionCorrelation(self.Re)
			self.dp = self.zeta * self.flowFactor * self.fState.rho * self.vFlow**2 / 2
		else:
			self.vFlow = 0
			self.Re = 0
			self.zeta = 0
			self.dp = 0
			
			
	def computeExitState(self, fStateOut):
		self.computePressureDrop()
		pOut = self.fState.p - self.dp
		fStateOut.update_Tp(self.TWall, pOut)
		dhMax = fStateOut.h - self.fState.h
		self.QDotWall = self.mDot * dhMax
		QDot = self.extWallArea * self.hConv * (self.TWall - self.fState.T)
		dh = QDot / self.mDot
		if (self.mDot > 1e-12):
			if (abs(dh) < abs(dhMax)):
				fStateOut.update_ph(pOut, self.fState.h + dh)
				self.QDotWall = QDot				 

class FluidChannel(object):
	def __init__(self, fFactory):
		self.fFactory = fFactory
		self.sections = []
	
	def addSection(self, section):
		section.fState = self.fFactory()
		self.sections.append(section)
	
	def setMDot(self, mDot):
		for section in self.sections:
			section.mDot = mDot
	
		
	def plotGeometry(self, ax = None, dy = 0):
		from matplotlib.collections import PatchCollection
		if (ax is None):
			fig = plt.figure()
			ax = fig.add_subplot(111)
		patches = []
		for sec in self.sections:
			sec.plotGeometry(patches)
		pc = PatchCollection(patches, match_original = True)
		ax.add_collection(pc)
		ax.set_xlim(0, self.sections[-1].xEnd)
		ax.set_ylim(-1e-2, 1e-2)
		
	def plotTemperature(self, ax = None, dy = 0):
		pass

def test():
	dtypeSections  = np.dtype([
		('length', np.float),
		('internalDiamater', np.float),
		('numDivisions', np.int),
	])
	extDiameter = 7e-3
	chanGeom = np.zeros((2,), dtype = dtypeSections)
	chanGeom[0] = (0.1, 1e-3, 10)
	chanGeom[1] = (0.2, 2e-3, 10)
	xStart = 0
	fc = FluidChannel('ParaHydrogen')
	for geomSection in chanGeom:
		dx = geomSection['length'] / geomSection['numDivisions']
		for i in range(geomSection['numDivisions']):
			section = FluidChannelSection(xStart + i * dx, xStart + (i + 1) * dx)
			section.setAnnularGeometry(geomSection['internalDiamater'], extDiameter)
			fc.addSection(section)
		xStart += geomSection['length']
	
	fc.plotGeometry()
	plt.show()
	
if __name__ == '__main__':
	test()