'''
Created on Feb 18, 2015

@author: Atanas Pavlov, Ivaylo Mihaylov
@copyright: SysMo Ltd., Bulgaria
'''
import numpy as np
from smo.media.CoolProp.CoolProp import FluidState, Fluid

class StateDiagram(object):
	def __init__(self, fluidName):
		self.fluidName = fluidName
		self.fluid = Fluid(fluidName)

class PHDiagram(StateDiagram):
	def setLimits(self, pMin = None, pMax = None,  hMin = None, hMax = None):
		# Reference points
		self.trippleLiquid = FluidState(self.fluid)
		self.trippleLiquid.update_pq(self.fluid.tripple['p'], 0)		
		self.trippleVapor = FluidState(self.fluid)
		self.trippleVapor.update_pq(self.fluid.tripple['p'], 1)
		self.critical = FluidState(self.fluid)
		self.critical.update_Trho(self.fluid.critical['T'], self.fluid.critical['rho'])

		# For general use
		fState = FluidState(self.fluid)

		# Pressure range
		if (pMin is None):
			pMin = self.fluid.tripple['p']
		self.pMin = pMin
		
		if (pMax is None):
			
			pMax =  10**(np.floor(np.log10(self.fluid.critical['p'])) + 2)
		self.pMax = pMax
		
		
		# Enthalpy range
		domeWidth = self.trippleVapor.h - self.trippleLiquid.h		
		if (hMin is None):
			hMin = self.trippleLiquid.h
		self.hMin = hMin
		
		if (hMax is None):
			hMax = self.trippleVapor.h + domeWidth
		self.hMax = hMax
		
		# Density range
		fState.update_ph(self.pMin, self.hMax)
		self.rhoMin = fState.rho
		self.rhoMax = self.trippleLiquid.rho
		print ("rho [{}: {}]".format(self.rhoMin, self.rhoMax))
		
		# Temperature range
		self.TMin = 1.01 * self.trippleLiquid.T
		fState.update_ph(self.pMin, self.hMax)
		self.TMax = fState.T
		
		# Entropy range
		self.sMin = 1.01 * self.trippleLiquid.s
		fState.update_ph(self.pMin, self.hMax)
		self.sMax = fState.s
	
	def plotDome(self):
		fState = FluidState(self.fluid)
		p = np.logspace(np.log10(self.pMin), np.log10(self.critical.p), num = 200)
		for q in np.arange(0, 1.1, 0.1):
			h = np.zeros(len(p))
			for i in range(len(p) - 1):
				fState.update_pq(p[i], q)
				h[i] = fState.h
			h[-1] = self.critical.h
			self.ax.semilogy(h/1e3, p/1e5, 'b')
			
	def plotIsochores(self):
		fState = FluidState(self.fluid)
		rhoArr1 = np.logspace(np.log10(self.rhoMin), np.log10(self.critical.rho), num = 20)
		rhoArr2 = np.logspace(np.log10(self.critical.rho), np.log10(self.rhoMax), num = 5)
		rhoArr = np.zeros(len(rhoArr1) + len(rhoArr2))
		rhoArr[:len(rhoArr1)] = rhoArr1[:]
		rhoArr[len(rhoArr1):] = rhoArr2[:]
		TArr = np.logspace(np.log10(self.TMin), np.log10(self.TMax), num = 100)
		for rho in rhoArr:
			hArr = np.zeros(len(TArr))
			pArr = np.zeros(len(TArr))
			for i in range(len(TArr)):
				fState.update_Trho(TArr[i], rho)
				hArr[i] = fState.h
				pArr[i] = fState.p
			self.ax.semilogy(hArr/1e3, pArr/1e5, 'g')
		
	def plotIsotherms(self):
		fState = FluidState(self.fluid)
		TArr = np.logspace(np.log10(self.TMin), np.log10(self.TMax), num = 20)
		fSatL = FluidState(self.fluidName)
		fSatV = FluidState(self.fluidName)
		f1 = FluidState(self.fluidName)
		for T in TArr:
			f1.update_Tp(T, self.pMax)
			if (T > self.critical.T):
				rhoArr1 = np.logspace(np.log10(self.rhoMin), np.log10(self.critical.rho), num = 100)
				rhoArr2 = np.logspace(np.log10(self.critical.rho), np.log10(f1.rho), num = 100)
			else:
				fSatL.update_Tq(T, 0)
				fSatV.update_Tq(T, 1)
				rhoArr1 = np.logspace(np.log10(self.rhoMin), np.log10(fSatV.rho), num = 100)
				rhoArr2 = np.logspace(np.log10(fSatL.rho), np.log10(f1.rho), num = 100)
			rhoArr = np.hstack((rhoArr1, rhoArr2))
			hArr = np.zeros(len(rhoArr))
			pArr = np.zeros(len(rhoArr))
			for i in range(len(rhoArr)):
				fState.update_Trho(T, rhoArr[i])
				hArr[i] = fState.h
				pArr[i] = fState.p
			self.ax.semilogy(hArr/1e3, pArr/1e5, 'r')
	
	def plotIsentrops(self):
		fState = FluidState(self.fluid)
		#sArr = np.linspace(self.sMin, self.sMax, num = 20)
		sArr = np.array([4000])
		TArr = np.logspace(np.log10(self.TMin), np.log10(self.TMax), num = 100)
		#TArr = np.logspace(np.log10(self.TMax), np.log10(self.TMin), num = 100)
		for s in sArr:
			hArr = np.zeros(len(TArr))
			pArr = np.zeros(len(TArr))
			rhoArr = np.zeros(len(TArr))
			fState.update_Ts(TArr[0], s)
			rhoArr[0] = fState.rho
			hArr[0] = fState.h
			pArr[0] = fState.p
			print ('----------------------------------------')
			print ('s=%e'%s)
			for i in range(1, len(TArr)):
				rhoArr[i] = rhoArr[i-1] + (TArr[i] - TArr[i-1]) * (rhoArr[i-1]**2) * fState.dsdt_v / fState.dpdt_v 
# 				if (rhoArr[i] <= 0):
# 					continue
				fState.update_Trho(TArr[i], rhoArr[i])
 				print ('rho: %e, T: %e, q: %e, s: %e'%(fState.rho, fState.T, fState.q, fState.s))
				hArr[i] = fState.h
				pArr[i] = fState.p
			self.ax.semilogy(hArr/1e3, pArr/1e5, 'bo')
			# Drawing (almost) middle line [s = 4000] by Ts
			hArr = np.zeros(len(TArr))
			pArr = np.zeros(len(TArr))
			for i in range(len(TArr)):
				fState.update_Ts(TArr[i], sArr[0])
				hArr[i] = fState.h
				pArr[i] = fState.p
				print ('rho by Ts: %e'%fState.rho)
			self.ax.semilogy(hArr/1e3, pArr/1e5, 'rx')
	
	def draw(self):
		import matplotlib.pyplot as plt
		fig = plt.figure()
		self.ax = fig.add_subplot(1,1,1)
		self.ax.set_xlim(self.hMin / 1e3, self.hMax / 1e3)
		self.ax.set_ylim(self.pMin / 1e5, self.pMax / 1e5)
		self.ax.set_xlabel('Enthalpy [kJ/kg]')
		self.ax.set_ylabel('Pressure [bar]')
		self.ax.set_title(self.fluidName)
		self.ax.grid(True)
		self.plotDome()
		#self.plotIsochores()
		#self.plotIsotherms()
		self.plotIsentrops()
		plt.show()


def main():
	#fluidList = ['R134a', 'IsoButane', 'Water', 'Oxygen', 'Nitrogen', 'CarbonDioxide', 'ParaHydrogen']
	fluidList = ['Water']	
	for fluid in fluidList:
		print("Calculating with fluid '{}'".format(fluid))
		diagram = PHDiagram(fluid)
		diagram.setLimits()
		diagram.draw()

if __name__ == '__main__':
	main()	
