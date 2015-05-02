'''
Created on Apr 23, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''

import math as m
import numpy as np
		
class StressTensorCalculator(object):
	@staticmethod
	def getRotationXTransf(theta):
		# source: http://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
		R = np.zeros((3, 3), dtype = np.float64)
		R[0, 0] = 1
		R[1, 1] = m.cos(theta)
		R[1, 2] = - m.sin(theta)
		R[2, 1] = m.sin(theta)
		R[2, 2] = m.cos(theta)
		return R

	@staticmethod
	def getRotationYTransf(theta):
		# source: http://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
		R = np.zeros((3, 3), dtype = np.float64)
		R[0, 0] = m.cos(theta)
		R[0, 2] = m.sin(theta)
		R[1, 1] = 1
		R[2, 0] = - m.sin(theta)
		R[2, 2] = m.cos(theta) 
		return R

	@staticmethod
	def getRotationZTransf(theta):
		# source: http://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
		R = np.zeros((3, 3), dtype = np.float64)
		R[0, 0] = m.cos(theta)
		R[0, 1] = - m.sin(theta)
		R[1, 0] = m.sin(theta)
		R[1, 1] = m.cos(theta)
		R[2, 2] =  1
		return R

	@staticmethod
	def getRotationTwoAngleTransf(theta, phi):
		"""
		source: Metal Fatigue Analysis Handbook: Practical problem-solving 
			techniques for computer aided engineering, p. 192, Eq. 5.48
		""" 
		R = np.zeros((3, 3))
		R[0, 0] = m.cos(theta) * m.sin(phi)
		R[0, 1] = m.sin(theta) * m.sin(phi)
		R[0, 2] = m.cos(phi)
		R[1, 0] = - m.sin(theta)
		R[1, 1] = m.cos(theta)
		R[1, 2] = 0
		R[2, 0] = - m.cos(theta) * m.cos(phi)
		R[2, 1] = - m.sin(theta) * m.cos(phi)
		R[2, 2] = m.sin(phi)
		
		return R
	
	@staticmethod
	def computePrincipalStresses(s):
		"""
		http://en.wikiversity.org/wiki/Principal_stresses
		"""
		#self.principalStressSeries =
		I1 = s[0, 0] + s[1, 1] + s[2, 2]
		I2 = s[0, 0] * s[1, 1] + s[1, 1] * s[2, 2] + s[2, 2] * s[0, 0] \
			- s[0, 1]**2 - s[1, 2]**2 - s[2, 0]**2
		I3 = s[0, 0] * s[1, 1] * s[2, 2] \
			- s[0, 0] * s[1, 2]**2 - s[1, 1] * s[2, 0]**2 - s[2, 2] * s[0, 1]**2 \
			+ 2 * s[0, 1] * s[1, 2] * s[2, 0]
		phiArg = (2 * I1 * I1 * I1 - 9 * I1 * I2 + 27 * I3) /\
				(2 * pow(I1 * I1 - 3 * I2, 3./2))
		if (phiArg < -1):
			phi = m.pi / 3
		elif (phiArg > 1):
			phi = 0
		else:
			phi = 1./3 * m.acos(phiArg)
		sp = np.zeros(3)
		for i in range(3):
			sp[i] = 1./3 * I1 + 2./3 * m.sqrt(I1 * I1 - 3 * I2) * m.cos(phi + 2./3 * m.pi * i) 
		sp.sort()
		return sp
	
	@staticmethod
	def computeTransformation(T, s):
		TPrim = np.dot(np.dot(T, s), T.T)
		return TPrim
