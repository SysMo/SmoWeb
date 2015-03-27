'''
Created on Feb 18, 2015

@author: Atanas Pavlov, Ivaylo Mihaylov
@copyright: SysMo Ltd., Bulgaria
'''
import numpy as np
import math
from smo.math.util import formatNumber
from smo.media.CoolProp.CoolProp import FluidState, Fluid
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os, tempfile
from SmoWeb.settings import MEDIA_ROOT
from collections import OrderedDict

PHDiagramFluids = OrderedDict((
	("Acetone", "Acetone"),
	("Ammonia", "Ammonia"),
	("Argon", "Argon"),
	("Benzene", "Benzene"),
	("IsoButane", "iso-Butane"),
	("n-Butane", "n-Butane"),
	("cis-2-Butene", "cis-2-Butene"),
	("trans-2-Butene", "trans-2-Butene"),
	("IsoButene", "iso-Butene"),
	("1-Butene", "1-Butene"),
	("CarbonDioxide", "Carbon dioxide"),
	("CarbonMonoxide", "Carbon monoxide"),
	("CarbonylSulfide", "Carbonyl sulfide"),
	("n-Decane", "n-Decane"),
	("Deuterium", "Deuterium"),
	("OrthoDeuterium", "ortho-Deuterium"),
	("ParaDeuterium", "para-Deuterium"),
	("DimethylCarbonate", "Dimethyl carbonate"),
	("DimethylEther", "Dimethyl ether"),
	("n-Dodecane", "n-Dodecane"),
	("D4", "D4"),
	("D5", "D5"),
	("D6", "D6"),
	("Ethane", "Ethane"),
	("Ethanol", "Ethanol"),
	("Ethylene", "Ethylene"),
	("EthylBenzene", "Ethyl benzene"),
	("Fluorine", "Fluorine"),
	("Helium", "Helium"),
	("CycloHexane", "cyclo-Hexane"),
	("Isohexane", "iso-Hexane"),
	("n-Hexane", "n-Hexane"),
	("n-Heptane", "n-Heptane"),
	("HFE143m", "HFE143m"),
	("Hydrogen", "normal-Hydrogen"),
	("OrthoHydrogen", "ortho-Hydrogen"),
	("ParaHydrogen", "para-Hydrogen"),
	("HydrogenSulfide", "Hydrogen sulfide"),
	("Krypton", "Krypton"),
	("Methane", "Methane"),
	("Methanol", "Methanol"),
	("MethylLinoleate", "Methyl linoleate"),
	("MethylLinolenate", "Methyl linolenate"),
	("MethylOleate", "Methyl oleate"),
	("MethylPalmitate", "Methyl palmitate"),
	("MethylStearate", "Methyl stearate"),
	("MD2M", "MD2M"),
	("MD3M", "MD3M"),
	("MD4M", "MD4M"),
	("MDM", "MDM"),
	("MM", "MM"),
	("Neon", "Neon"),
	("Nitrogen", "Nitrogen"),
	("NitrousOxide", "Nitrous oxide"),
	("n-Nonane", "n-Nonane"),
	("n-Octane", "n-Octane"),
	("Oxygen", "Oxygen"),
	("Cyclopentane", "cyclo-Pentane"),
	("Isopentane", "iso-Pentane"),
	("n-Pentane", "n-Pentane"),
	("Neopentane", "neo-Pentane"),
	("CycloPropane", "cyclo-Propane"),
	("n-Propane", "n-Propane"),
	("Propylene", "Propylene"),
	("R11", "R11"),
	("R113", "R113"),
	("R114", "R114"),
	("R116", "R116"),
	("R12", "R12"),
	("R123", "R123"),
	("R1233zd(E)", "R1233zd(E)"),
	("R1234yf", "R1234yf"),
	("R1234ze(Z)", "R1234ze(Z)"),
	("R124", "R124"),
	("R125", "R125"),
	("R13", "R13"),
	("R134a", "R134a"),
	("R14", "R14"),
	("R141b", "R141b"),
	("R142b", "R142b"),
	("R143a", "R143a"),
	("R152A", "R152A"),
	("R161", "R161"),
	("R161", "R161"),
	("R21", "R21"),
	("R218", "R218"),
	("R22", "R22"),
	("R227EA", "R227EA"),
	("R23", "R23"),
	("R236EA", "R236EA"),
	("R236FA", "R236FA"),
	("R245fa", "R245fa"),
	("R32", "R32"),
	("R365MFC", "R365MFC"),
	("R41", "R41"),
	("RC318", "RC318"),
	("SulfurDioxide", "SulfurDioxide"),
	("SulfurHexafluoride", "SulfurHexafluoride"),
	("Toluene", "Toluene"),
	("n-Undecane", "n-Undecane"),
	("Water", "Water"),
	("Xenon", "Xenon"),
	("m-Xylene", "m-Xylene"),
	("o-Xylene", "o-Xylene"),
	("p-Xylene", "p-Xylene"),
))


class StateDiagram(object):
	def __init__(self, fluidName):
		self.fluidName = fluidName
		self.fluid = Fluid(fluidName)
	
	def getLabelPlacement(self, x1, x2, y1, y2, xlog = False, ylog = True, d = 3):
		if (xlog == True):
			frac_range_x = np.log10(x2/x1) / np.log10(self.xMax/self.xMin)
		else:	
			frac_range_x = (x2 - x1) / (self.xMax - self.xMin)
		if (ylog == True):
			frac_range_y = np.log10(y2/y1) / np.log10(self.yMax/self.yMin)
		else:
			frac_range_y = (y2 - y1) / (self.yMax - self.yMin)
		
		delta_x = frac_range_x  * self.x_pts
		delta_y = frac_range_y * self.y_pts
		
		alpha = math.atan(delta_y / delta_x)
		s = math.sqrt(delta_x**2 + delta_y**2)
		e = math.sqrt(s**2 / 4. + d**2)
		
		beta = math.atan(2 * d / s)
		gamma = math.radians(90) - alpha - beta
		
		offset_x = e * math.sin(gamma)
		offset_y = e * math.cos(gamma)
		
		alpha = math.degrees(alpha)
		return (alpha, offset_x, offset_y)

class PHDiagram(StateDiagram):
	def __init__(self, fluidName, temperatureUnit = 'K'):
		super(PHDiagram, self).__init__(fluidName)
		self.temperatureUnit = temperatureUnit
	
	def setLimits(self, pMin = None, pMax = None,  hMin = None, hMax = None, TMax = None):
		# Reference points
		self.minLiquid = FluidState(self.fluid)
		self.minVapor = FluidState(self.fluid)
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
		
		self.minLiquid.update_pq(self.pMin, 0)		
		self.minVapor.update_pq(self.pMin, 1)
		
		if (pMax is None):
			pMax = 3 * self.critical.p
		self.pMax = pMax
		
		
		# Enthalpy range
		domeWidth = self.minVapor.h - self.minLiquid.h		
		if (hMin is None):
			hMin = self.minLiquid.h
		self.hMin = hMin
		
		# Determining max enthalpy
		if (TMax is None):
			if (hMax is None):
				# default max enthalpy	
				if (self.critical.h > self.minVapor.h):
					hMax = self.critical.h + domeWidth
				else:
					hMax = self.minVapor.h + domeWidth
		else:
			fState.update_Tp(TMax, self.pMin)
			hMax = fState.h
			
		self.hMax = hMax
		
		# Axes ranges
		self.xMin = self.hMin
		self.xMax = self.hMax
		self.yMin = self.pMin
		self.yMax = self.pMax
		
		# Density range
		fState.update_ph(self.pMin, self.hMax)
		self.rhoMin = fState.rho
		self.rhoMax = self.minLiquid.rho
		
		# Temperature range
		self.TMin = self.fluid.saturation_p(self.pMin)["TsatL"]
		
		if (TMax is None):
			fState.update_ph(self.pMin, self.hMax)
			TMax = fState.T
		self.TMax = TMax
		
		# Entropy range
		self.sMin = 1.01 * self.minLiquid.s
		
		fState.update_ph(self.pMin, self.hMax)
		self.sMax = fState.s
		
		# Minor diagonal coeff
		self.minDiagonalSlope = np.log10(self.pMax/self.pMin) / (self.hMax - self.hMin) * 1e3
		
		# Major diagonal coeff
		self.majDiagonalSlope = - self.minDiagonalSlope
	
	def plotDome(self):
		fState = FluidState(self.fluid)
		p = np.logspace(np.log10(self.pMin), np.log10(self.critical.p), num = 200)
		qLabels = ['0.2', '0.4', '0.6', '0.8']
		for q in np.arange(0, 1.1, 0.1):
			try:
				h = np.zeros(len(p))
				for i in range(len(p) - 1):
					fState.update_pq(p[i], q)
					h[i] = fState.h
				# Putting labels
				if '{:1.1f}'.format(q) in qLabels:
					angle, offset_x, offset_y = self.getLabelPlacement(x1 = h[9], x2 = h[10],
											y1 = p[9], y2 = p[10])
					self.ax.annotate("{:1.1f}".format(q), 
									xy = (h[10]/ 1e3, p[10] / 1e5),
									xytext=(-offset_x, -offset_y),
									textcoords='offset points',
									color='b', size="small", rotation = angle)
				h[-1] = self.critical.h
				if (q == 0):			
					self.ax.semilogy(h/1e3, p/1e5, 'b', label = 'vapor quality')
				else:
					self.ax.semilogy(h/1e3, p/1e5, 'b')
			except RuntimeError, e:
				print '------------------'
				print 'Runtime Warning for q=%e'%q 
				print(e)
			
	def plotIsochores(self):
		fState = FluidState(self.fluid)
		rhoArr1 = np.logspace(np.log10(self.rhoMin), np.log10(self.critical.rho), num = 20, endpoint = False)
		rhoArr2 = np.logspace(np.log10(self.critical.rho), np.log10(self.rhoMax), num = 5)
		rhoArr = np.zeros(len(rhoArr1) + len(rhoArr2))
		rhoArr[:len(rhoArr1)] = rhoArr1[:]
		rhoArr[len(rhoArr1):] = rhoArr2[:]
		TArr = np.logspace(np.log10(self.TMin), np.log10(self.TMax), num = 100)
		# For label location purposes
		h_level_low = self.hMin + (self.critical.h - self.hMin) * 3 / 4.
		h_level_high = self.critical.h + (self.hMax - self.critical.h) * 1 / 2. 
		for rho in rhoArr:
			try:
				hArr = np.zeros(len(TArr))
				pArr = np.zeros(len(TArr))
				for i in range(len(TArr)):
					fState.update_Trho(TArr[i], rho)
					hArr[i] = fState.h
					pArr[i] = fState.p
					# Putting labels
					# Determining annotated point and label text offest
					
					if (pArr[i-1] < self.pMax and pArr[i] > self.pMax):
						if (hArr[i] < h_level_low):
							angle, offset_x, offset_y = self.getLabelPlacement(x1 = hArr[i-1], x2 = hArr[i],
																				y1 = pArr[i-1], y2 = pArr[i])
							self.ax.annotate(formatNumber(rho, sig = 2), 
											xy = (hArr[i-1] / 1e3, pArr[i-1] / 1e5),
											xytext=(0, -10),
											textcoords='offset points',
											color='g', size="small", rotation = angle)
						elif (hArr[i] > h_level_low and hArr[i] < h_level_high):
							angle, offset_x, offset_y = self.getLabelPlacement(x1 = hArr[i-2], x2 = hArr[i-1],
																				y1 = pArr[i-2], y2 = pArr[i-1])
							self.ax.annotate(formatNumber(rho, sig = 2), 
											xy = (hArr[i-2] / 1e3, pArr[i-2] / 1e5),
											xytext=(5, -5),
											textcoords='offset points',
											color='g', size="small", rotation = angle)
						elif (hArr[i] > h_level_high):
							angle, offset_x, offset_y = self.getLabelPlacement(x1 = hArr[i-10], x2 = hArr[i-9],
																				y1 = pArr[i-10], y2 = pArr[i-9])
							self.ax.annotate(formatNumber(rho, sig = 2), 
											xy = (hArr[i-10] / 1e3, pArr[i-10] / 1e5),
											xytext=(0, -5),
											textcoords='offset points',
											color='g', size="small", rotation = angle)
					elif (i == len(TArr) - 1 and pArr[i] < self.pMax and pArr[i-1] > self.pMin):
						angle, offset_x, offset_y = self.getLabelPlacement(x1 = hArr[i-1], x2 = hArr[i],
																			y1 = pArr[i-1], y2 = pArr[i])
						self.ax.annotate(formatNumber(rho, sig = 2), 
										xy = (hArr[i] / 1e3, pArr[i] / 1e5),
										xytext=(-30, -12),
										textcoords='offset points',
										color='g', size="small", rotation = angle)
				if (rho == rhoArr[0]):
					self.ax.semilogy(hArr/1e3, pArr/1e5, 'g', label = 'density [kg/m3]')
				else:
					self.ax.semilogy(hArr/1e3, pArr/1e5, 'g')
			except RuntimeError, e:
				print '------------------'
				print 'Runtime Warning for rho=%e'%rho 
				print(e)
		
	def plotIsotherms(self):
		fState = FluidState(self.fluid)
		TArr = np.logspace(np.log10(self.TMin), np.log10(self.TMax), num = 20)
		TOrders = np.floor(np.log10(TArr))
		TArr = np.ceil(TArr / 10**(TOrders - 2)) * 10**(TOrders - 2)
		fSatL = FluidState(self.fluidName)
		fSatV = FluidState(self.fluidName)
		f1 = FluidState(self.fluidName)
		for T in TArr:
			if self.temperatureUnit == 'degC':
				T_label = T  - 273.15
			else:
				T_label = T
			try:
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
							self.ax.annotate(formatNumber(T_label, sig = 3), 
											xy = ((fSatL.h + fSatV.h) / 2. / 1e3, pArr[i] / 1e5),
											xytext=(0, 3),
											textcoords='offset points',
											color='r', size="small")
					else:
						if (i>0):
							b = np.log10(self.pMin / 1e5) - self.minDiagonalSlope * self.hMin / 1e3
							if (np.log10(pArr[i-1] / 1e5) - self.minDiagonalSlope * hArr[i-1] / 1e3 - b) * \
								(np.log10(pArr[i] / 1e5) - self.minDiagonalSlope * hArr[i] / 1e3 - b) <= 0:
								# Getting label rotation angle
								angle, offset_x, offset_y = self.getLabelPlacement(x1 = hArr[i-1], x2 = hArr[i],
																					y1 = pArr[i-1], y2 = pArr[i])
								self.ax.annotate(formatNumber(T_label, sig = 3), 
												xy = (hArr[i]/1e3, pArr[i]/1e5),
												xytext=(offset_x, offset_y),
												textcoords='offset points',
												color='r', size="small", rotation = angle)
				
				if (T == TArr[0]):
					if self.temperatureUnit == 'degC':
						label = "temperature [C]"
					else:
						label = "temperature [K]"
					self.ax.semilogy(hArr/1e3, pArr/1e5, 'r', label = label)
				else:
					self.ax.semilogy(hArr/1e3, pArr/1e5, 'r')
			except RuntimeError, e:
				print '------------------'
				print 'Runtime Warning for T=%e'%T 
				print(e)
	
	def plotIsentrops(self):
		fState = FluidState(self.fluid)
		sArr = np.linspace(self.sMin, self.sMax, num = 20)
		for s in sArr:
			try:
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
				while (T > self.TMin):
					_dvdT_s = - fState.dsdT_v / fState.dpdT_v
					if math.isnan(_dvdT_s ):
						break
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
					hArr.append(fState.h)
					pArr.append(fState.p)
					##################
					# Putting labels
					i = len(hArr) - 1
					b = np.log10(self.pMax / 1e5) - self.majDiagonalSlope * self.hMin / 1e3
					if (np.log10(pArr[i-1] / 1e5) - self.majDiagonalSlope * hArr[i-1] / 1e3 - b) * \
						(np.log10(pArr[i] / 1e5) - self.majDiagonalSlope * hArr[i] / 1e3 - b) <= 0:
						angle, offset_x, offset_y = self.getLabelPlacement(x1 = hArr[i-1], x2 = hArr[i],
																			y1 = pArr[i-1], y2 = pArr[i])
						self.ax.annotate(formatNumber(s/1e3, sig = 3), 
											xy = (hArr[i-1]/1e3, pArr[i-1]/1e5),
											xytext=(-offset_x, -offset_y),
											textcoords='offset points',
											color='m', size="small", rotation = angle)
					#######################
				hArr = np.array(hArr)
				pArr = np.array(pArr)
				if (s == sArr[0]):
					self.ax.semilogy(hArr/1e3, pArr/1e5, 'm', label = "entropy [kJ/kg-K]")
				else:
					self.ax.semilogy(hArr/1e3, pArr/1e5, 'm')
			except RuntimeError, e:
				print '------------------'
				print 'Runtime Warning for s=%e'%s 
				print e
	
	def draw(self, isotherms=True, isochores=True, isentrops=True, qIsolines=True, fig = None):
		if (fig is None):
			fig = Figure(figsize=(16.0, 10.0))
		self.fig = fig
		self.ax = self.fig.add_subplot(1,1,1)
		self.ax.set_xlabel('Enthalpy [kJ/kg]')
		self.ax.set_ylabel('Pressure [bar]')
		self.ax.set_title(self.fluidName, y=1.04)
		self.ax.grid(True, which = 'both')
		
		x_in, y_in = self.fig.get_size_inches()
		dpi = self.fig.get_dpi()
		self.x_pts = x_in * dpi
		self.y_pts = y_in * dpi
		
		self.ax.set_xlim(self.hMin / 1e3, self.hMax / 1e3)
		self.ax.set_ylim(self.pMin / 1e5, self.pMax / 1e5)
		
		if qIsolines:
			self.plotDome()
		if isochores:
			self.plotIsochores()
		if isotherms:
			self.plotIsotherms()
		if isentrops:
			self.plotIsentrops()
		
		self.ax.legend(loc='upper center',  bbox_to_anchor=(0.5, 1.05),  fontsize="small", ncol=4)
		return fig
	
	def export(self, fig):
		fileHandler, absFilePath = tempfile.mkstemp('.png', dir = os.path.join(MEDIA_ROOT, 'tmp'))
		resourcePath = os.path.join('media', os.path.relpath(absFilePath, MEDIA_ROOT))
		canvas = FigureCanvas(fig)
		canvas.print_png(absFilePath)
		return (fileHandler, resourcePath)
	
	
def main():
	FluidsSample = ['R134a',  'Water', 'Oxygen', 'Nitrogen', 'CarbonDioxide', 'ParaHydrogen', 'IsoButane']
	# Fluids throwing RuntimeError
	ExcludedFluids = ['Air', 'Propyne', 'R1234ze(E)']
	
	fluidList = ['ParaHydrogen']
	for i in range(len(fluidList)):
		fluid = fluidList[i]
		print("{}. Calculating with fluid '{}'".format(i, fluid))
		diagram = PHDiagram(fluid)
		diagram.setLimits()
		import pylab as plt
		fig = plt.figure()
		diagram.draw(isotherms = True, isochores = True, isentrops = True, qIsolines = True, fig = fig)
		plt.show()
if __name__ == '__main__':
	main()	
