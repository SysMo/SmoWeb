'''
Created on Mar 5, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import unittest
from smo.media.CoolProp.CoolProp import FluidState
from Structures import *
from FlowComponents import FluidHeater
from SourcesSinks import FlowSource, FluidStateSource, TemperatureSource
from HeatFlowComponents import TwoPortHeatTransfer
"""
======================================
Structures.py
======================================
"""

class TestStructures(unittest.TestCase):
	def setUp(self):
		fState = FluidState('Oxygen')
		tState = ThermalState()
		self.fp1 = FluidPort('C', fState)
		self.fp2 = FluidPort('R')
		self.fp3 = DynamicCPort(FluidPort, FluidState('Oxygen'))
		self.fp4 = FluidPort('R')
		self.tp1 = ThermalPort('C', tState)
		self.tp2 = ThermalPort('R')
		self.tp3 = ThermalPort('R')
		
		self.fp1.state.update_Tp(300, 2e5)
		self.fp2.flow.mDot = 3.0
		self.fp2.flow.HDot = 4.0e3
		self.fp4.flow.mDot = 5.0
		self.fp4.flow.HDot = 7.0e3
		self.tp1.state.T = 23
		self.tp2.flow.QDot = 2.0e3

	def test1(self):
		self.fp1.connect(self.fp2)
		self.assertAlmostEqual(self.fp1.flow.mDot, self.fp2.flow.mDot)
		self.assertAlmostEqual(self.fp1.flow.HDot, self.fp2.flow.HDot)
		self.assertAlmostEqual(self.fp1.state.T, self.fp2.state.T)
		self.tp1.connect(self.tp2)
		self.assertAlmostEqual(self.tp1.flow.QDot, self.tp2.flow.QDot)
		self.assertAlmostEqual(self.tp1.state.T, self.tp2.state.T)
		
	def test2(self):
		with self.assertRaises(ValueError):
			self.fp1.connect(self.tp2)
		
	def test3(self):
		with self.assertRaises(ValueError):
			self.tp2.connect(self.tp3)
			
	def test4(self):
		self.fp2.connect(self.fp3)
		self.fp3.connect(self.fp4)
		self.assertAlmostEqual(self.fp3.flow.mDot, self.fp2.flow.mDot + self.fp4.flow.mDot)
		self.assertAlmostEqual(self.fp3.flow.HDot, self.fp2.flow.HDot + self.fp4.flow.HDot)
		
	def test5(self):
		fp4_rev = - self.fp4.flow
		self.assertAlmostEqual(fp4_rev.mDot, - self.fp4.flow.mDot)
		self.assertAlmostEqual(fp4_rev.HDot, - self.fp4.flow.HDot)
		tp2_rev = - self.tp2.flow
		self.assertAlmostEqual(tp2_rev.QDot, - self.tp2.flow.QDot)
		
"""
======================================
FlowComponents.py
======================================
"""
class TestsFlowComponents(unittest.TestCase):
	def setUp(self):
		self.fluid = 'Nitrogen'
		
	def testFluidHeater(self):
		fh = FluidHeater(self.fluid)
		TFluid = 290.0
		fs1 = FlowSource(self.fluid, mDot = 0.1, TOut = TFluid)
		fs2 = FluidStateSource(self.fluid, sourceType = FluidStateSource.TP)
		tp = ThermalPort('C', ThermalState(T = 350))
		fh.portOut.connect(fs2.port1)
		fh.portIn.connect(fs1.port1)
		fh.thermalPort.connect(tp)
		fs2.TIn = 288.0
		fs2.pIn = 1e5
		
		fs2.computeState()
		fh.setState()
		fs1.compute()
		fh.compute()

		self.assertAlmostEqual(fh.QDot, 100* (TFluid - tp.state.T))
		self.assertAlmostEqual(fh.QDot, fs1.port1.flow.HDot - fs2.port1.flow.HDot)
		self.assertAlmostEqual(fh.portOut.state.p, fh.portIn.state.p)
		
"""
======================================
HeatFlowComponents.py
======================================
"""
class TestHeatFlowComponents(unittest.TestCase):
	def setUp(self):
		pass
	def testTwoPortHeatTransfer(self):
		t1 = TemperatureSource(T = 300.)
		t2 = TemperatureSource(T = 250.)
		t1.computeState()
		t2.computeState()
		def condModel(T1, T2):
			if (T2 > 80.):
				return (10. * (T1 - T2))
			else:
				return 2000.0
		c = TwoPortHeatTransfer(condModel = condModel)
		c.port1.connect(t1.port1)
		c.port2.connect(t2.port1)
		c.compute()
		self.assertAlmostEqual(t1.port1.flow.QDot, -500.)
		self.assertAlmostEqual(t2.port1.flow.QDot, 500.)

		t2.T = 60.
		t2.computeState()
		c.compute()
		self.assertAlmostEqual(t1.port1.flow.QDot, -2000.)
		self.assertAlmostEqual(t2.port1.flow.QDot, 2000.)
		