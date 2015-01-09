'''
Created on Jan 5, 2015

@author: Atanas Pavlov
@copyright: SysMo Ltd.
'''
import numpy as np
from smo.model.model import NumericalModel
from smo.model.fields import *
from smo.media.MaterialData import Solids
from collections import OrderedDict
import fipy as fp
from fipy.solvers.pysparse import LinearLUSolver

class RadialHeatTransferSolver(object):
	"""
	Solver for axi-symmetrical radial heat transfer (1.5D) in a plane object
	with convection to ambient.
	"""
	def __init__(self, thermalConductivity, TAmb, thickness):
		"""
		:param float thermalConductivity: thermal conductivity of the material
		:param float TAmb: ambient temperature
		:param float thickness: thickness of the 
		"""
		self.TAmb = TAmb
		self.thermalConductivity = thermalConductivity
		self.thickness = thickness
		self.convection = {
			'active': False,
			'coefficient': 1.0,
		}
		self.solverSettings = {
			'nonlinear': False,
			'tolerance': 1e-6,
			'maxIterations': 50,
			'relaxationFactor': 0.99
		}
		self.BC = [
			{'type': 'Q', 'flux': 0},
			{'type': 'Q', 'flux': 0},
		]
	
	def createMesh(self, rIn, rOut, n = 100):
		"""Creates the radial (1D) mesh"""
		dx = float(rOut - rIn) / n
		self.mesh = fp.CylindricalGrid1D(origin = rIn, nx = n, dx = dx)
		print ("oops")

	@property
	def areaExtFaces(self):
		"""Computes areas of the external faces (used for convection)"""
		faceCenters = self.mesh.faceCenters()[0]
		faceAreas = np.pi * (faceCenters[1:] ** 2 - faceCenters[:-1] ** 2)
		return faceAreas
	
	@property
	def areaFaces(self):
		"""Computes areas of the radial faces (used for conduction)"""
		return 2 * np.pi * self.mesh.faceCenters() * self.thickness
	
	@property
	def faceDistances(self):
		return np.diff(self.mesh.faceCenters()[0])
	
	@property
	def QAx(self):
		return fp.FaceVariable(mesh = self.mesh, 
			value = - self.thermalConductivity * self.areaFaces * self.T.faceGrad)

	@property
	def QConv(self):
		if (self.convection['active']):
			value = self.convection['coefficient'] * self.mesh.fac * (self.T() - self.TAmb) \
				 * self.areaExtFaces / self.faceDistances
		else:
			value = np.zeros(self.T().shape)
		return value
	
	@property
	def QConvSum(self):
		return np.sum(self.QConv * self.faceDistances)

	@property
	def maxT(self):
		return np.max(self.T.arithmeticFaceValue())

	def applyBC(self, faces, bcDef, area = None):
		if (bcDef['type'] == 'T'):
			self.T.constrain(bcDef['temperature'], faces)
		elif (bcDef['type'] == 'Q'):
			gradValue = bcDef['flux'] / area / self.thermalConductivity
			self.T.faceGrad.constrain([-gradValue], faces)			
		else:
			raise NotImplementedError('Boundary conditions type "{0}" is not implemented'.format(bcDef[type]))

	
	@classmethod
	def test(cls):
		s = RadialHeatTransferSolver(thermalConductivity = 10, TAmb = 300, thickness = 5e-3)
		s.createMesh(0.1, 1, 9)
		print ("areaFaces: ", s.areaFaces)
		print ("areaExtFaces: ", s.areaExtFaces)
		print ("faceDistance", s.faceDistances)

if __name__ == "__main__":
	RadialHeatTransferSolver.test()	