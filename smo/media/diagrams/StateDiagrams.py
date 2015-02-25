'''
Created on Feb 18, 2015

@author: Atanas Pavlov, Ivaylo Mihaylov
@copyright: SysMo Ltd., Bulgaria
'''
import numpy as np
import math
from smo.media.CoolProp.CoolProp import FluidState, Fluid
import matplotlib.pyplot as plt

class StateDiagram(object):
	def __init__(self, fluidName):
		self.fluidName = fluidName
		self.fluid = Fluid(fluidName)
	
	def getLabelAngle(self, x1, x2, xmin, xmax, y1, y2, ymin, ymax, xlog = False, ylog = True):
		if (xlog == True):
			frac_range_x = np.log10(x2/x1) / np.log10(xmax/xmin)
		else:	
			frac_range_x = (x2 - x1) / (xmax - xmin)
		if (ylog == True):
			frac_range_y = np.log10(y2/y1) / np.log10(ymax/ymin)
		else:
			frac_range_y = (y2 - y1) / (ymax - ymin)
		
		return math.degrees(math.atan(0.7 * frac_range_y / frac_range_x))

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
			pMin = self.fluid.tripple['p'] * 1.05
			if (pMin < 1e3):
				pMin = 1e3
		self.pMin = pMin
		
		
		if (pMax is None):
			pMax =  10**(np.floor(np.log10(self.critical.p)) + 1.0)
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
		#print ("rho [{}: {}]".format(self.rhoMin, self.rhoMax))
		
		# Temperature range
		self.TMin = self.fluid.saturation_p(self.pMin)["TsatL"]
		fState.update_ph(self.pMin, self.hMax)
		self.TMax = fState.T
		
		# Entropy range
		self.sMin = 1.01 * self.trippleLiquid.s
		fState.update_ph(self.pMin, self.hMax)
		self.sMax = fState.s
		print ('sMin={}, sMax={}'.format(self.sMin, self.sMax))
		
		# Minor diagonal coeff
		self.minDiagonalSlope = np.log10(self.pMax/self.pMin) / (self.hMax - self.hMin) * 1e3
		
		# Major diagonal coeff
		self.majDiagonalSlope = - self.minDiagonalSlope
	
	def plotDome(self):
		fState = FluidState(self.fluid)
		p = np.logspace(np.log10(self.pMin), np.log10(self.critical.p), num = 200)
		qLabels = ['0.2', '0.4', '0.6', '0.8']
		for q in np.arange(0, 1.1, 0.1):
			h = np.zeros(len(p))
			for i in range(len(p) - 1):
				fState.update_pq(p[i], q)
				h[i] = fState.h
			# Putting labels
			angle = self.getLabelAngle(x1 = h[9], x2 = h[10],
										xmin = self.hMin, xmax = self.hMax,
										y1 = p[9], y2 = p[10],
										ymin = self.pMin, ymax = self.pMax)
			
			if '{:1.1f}'.format(q) in qLabels:
				self.ax.annotate("{:1.1f}".format(q), 
								xy = (h[10]/ 1e3, p[10] / 1e5),
								xytext=(-12, 0),
								textcoords='offset points',
								color='b', size="small", rotation = angle)
			h[-1] = self.critical.h			
			self.ax.semilogy(h/1e3, p/1e5, 'b')
			
	def plotIsochores(self):
		fState = FluidState(self.fluid)
		rhoArr1 = np.logspace(np.log10(self.rhoMin), np.log10(self.critical.rho), num = 20, endpoint = False)
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
				# Putting labels
				h_level_low = self.hMin + (self.critical.h - self.hMin) * 1 / 4.
				h_level_high = self.critical.h + (self.hMax - self.critical.h) * 1 / 2. 
				angle = self.getLabelAngle(x1 = hArr[i-1], x2 = hArr[i],
											xmin = self.hMin, xmax = self.hMax,
											y1 = pArr[i-1], y2 = pArr[i],
											ymin = self.pMin, ymax = self.pMax)
				
				# Determining label offset off annotated point based on the point's location on the figure
				if (pArr[i-1] < self.critical.p and pArr[i] > self.critical.p
					and hArr[i] < h_level_low):
					self.ax.annotate("{:2.1f}".format(rho), 
									xy = (hArr[i] / 1e3, pArr[i] / 1e5),
									xytext=(-20, -5),
									textcoords='offset points',
									color='g', size="small", rotation = angle)
				elif (pArr[i-1] < self.critical.p and pArr[i] > self.critical.p
					and hArr[i] > h_level_low and hArr[i] < h_level_high):
					self.ax.annotate("{:2.1f}".format(rho), 
									xy = (hArr[i] / 1e3, pArr[i] / 1e5),
									xytext=(-15, 10),
									textcoords='offset points',
									color='g', size="small", rotation = angle)
				elif (hArr[i-1] < h_level_high and hArr[i] > h_level_high 
					and pArr[i] < self.critical.p):
					self.ax.annotate("{:2.1f}".format(rho), 
									xy = (hArr[i] / 1e3, pArr[i] / 1e5),
									xytext=(-3, 7),
									textcoords='offset points',
									color='g', size="small", rotation = angle)
			self.ax.semilogy(hArr/1e3, pArr/1e5, 'g')
		
	def plotIsotherms(self):
		fState = FluidState(self.fluid)
		TArr = np.logspace(np.log10(self.TMin), np.log10(self.TMax), num = 20)
		TOrders = np.floor(np.log10(TArr))
		TArr = np.ceil(TArr / 10**(TOrders - 2)) * 10**(TOrders - 2)
		
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
				# Determining label location
				if (T < self.critical.T):
					if (i == len(rhoArr1)):
						self.ax.annotate("{:3.0f}".format(T), 
										xy = ((fSatL.h + fSatV.h) / 2. / 1e3, pArr[i] / 1e5),
										xytext=(0, 3),
										textcoords='offset points',
										color='r', size="small")
				else:
					b = np.log10(self.pMin / 1e5) - self.minDiagonalSlope * self.hMin / 1e3
					if (np.log10(pArr[i-1] / 1e5) - self.minDiagonalSlope * hArr[i-1] / 1e3 - b) * \
						(np.log10(pArr[i] / 1e5) - self.minDiagonalSlope * hArr[i] / 1e3 - b) < 0:
						# Getting label rotation angle
						angle = self.getLabelAngle(x1 = hArr[i-1], x2 = hArr[i],
													xmin = self.hMin, xmax = self.hMax,
													y1 = pArr[i-1], y2 = pArr[i],
													ymin = self.pMin, ymax = self.pMax)
						self.ax.annotate("{:3.0f}".format(T), 
										xy = (hArr[i]/1e3, pArr[i]/1e5),
										xytext=(0, 3),
										textcoords='offset points',
										color='r', size="small", rotation = angle)
			self.ax.semilogy(hArr/1e3, pArr/1e5, 'r')
	
	def plotIsentrops(self):
		fState = FluidState(self.fluid)
		sArr = np.linspace(self.sMin, self.sMax, num = 20)
		for s in sArr:
			hArr = []
			pArr = []
			fState.update_ps(self.pMax, s)
			if (fState.T > self.TMax):
				fState.update_Ts(self.TMax, s)
			T = fState.T
			hArr.append(fState.h)
			pArr.append(fState.p)
			# Calculated v
			v_res = fState.v
			print ('----------------------------------------')
			print ('s=%e'%s)
			while (T > self.TMin):
				_dvdT_s = - fState.dsdT_v / fState.dpdT_v
				TStep = - (self.critical.T / 200.) / (np.abs(_dvdT_s) + 1) 
				T = T + TStep
				if T < self.TMin:
					break
				v_res += _dvdT_s * TStep
				fState.update_Trho(T, 1. / v_res)
				p = fState.p
				# If it goes out of the screen through the bottom
				if (p < self.pMin):
					break
				# Calculated s
				s_res = fState.s
				# Correcting v
				ds = s - s_res
				sigma = ds * fState.dvds_T
				v = v_res + sigma
				fState.update_Trho(T, 1. / v)
				#print(T, p/1e5, s_res, fState.s)
 				#print ('rho: %e, T: %e, q: %e, s: %e'%(fState.rho, fState.T, fState.q, fState.s))
				hArr.append(fState.h)
				pArr.append(fState.p)
			hArr = np.array(hArr)
			pArr = np.array(pArr)
			print("Num points: {}".format(len(pArr)))
			print("Final s: {}".format(fState.s))
			print - fState.dsdT_v / fState.dpdT_v
			self.ax.semilogy(hArr/1e3, pArr/1e5, 'm')
# 		# Drawing (almost) middle line [s = 4000] by Ts
# 		for s in sArr:
# 			TArr = np.linspace(self.TMax, self.TMin, num = 100)
# 			hArr = np.zeros(len(TArr))
# 			pArr = np.zeros(len(TArr))
# 			for i in range(len(TArr)):
# 				fState.update_Ts(TArr[i], s)
# 				hArr[i] = fState.h
# 				pArr[i] = fState.p
# 				#print ('rho by Ts: %em T: %e'%(fState.rho, TArr[i]))
# 				self.ax.semilogy(hArr/1e3, pArr/1e5, 'r')
	
	def draw(self):
		fig = plt.figure()
		self.ax = fig.add_subplot(1,1,1)
		self.ax.set_xlim(self.hMin / 1e3, self.hMax / 1e3)
		self.ax.set_ylim(self.pMin / 1e5, self.pMax / 1e5)
		self.ax.set_xlabel('Enthalpy [kJ/kg]')
		self.ax.set_ylabel('Pressure [bar]')
		self.ax.set_title(self.fluidName)
		self.ax.grid(True, which = 'both')
		self.plotDome()
		self.plotIsochores()
		self.plotIsotherms()
		self.plotIsentrops()
		plt.show()


def main():
	fluidList = ['R134a',  'Water', 'Oxygen', 'Nitrogen', 'CarbonDioxide', 'ParaHydrogen', 'IsoButane']
	#fluidList = ['Oxygen', 'ParaHydrogen', 'IsoButane']	
	for fluid in fluidList:
		print("Calculating with fluid '{}'".format(fluid))
		diagram = PHDiagram(fluid)
		diagram.setLimits()
		diagram.draw()

if __name__ == '__main__':
	main()	
