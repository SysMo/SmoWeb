'''
Created on Mar 5, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import unittest
from smo.media.CoolProp.CoolProp import FluidState
from Structures import *
"""
======================================
Structures.py
======================================
"""

class TestRCPort(unittest.TestCase):
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
		self.tp2.flow.qDot = 2.0e3

	def test1(self):
		self.fp1.connect(self.fp2)
		self.assertAlmostEqual(self.fp1.flow.mDot, self.fp2.flow.mDot)
		self.assertAlmostEqual(self.fp1.flow.HDot, self.fp2.flow.HDot)
		self.assertAlmostEqual(self.fp1.state.T, self.fp2.state.T)
		self.tp1.connect(self.tp2)
		self.assertAlmostEqual(self.tp1.flow.qDot, self.tp2.flow.qDot)
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
		self.assertAlmostEqual(tp2_rev.qDot, - self.tp2.flow.qDot)
		
		