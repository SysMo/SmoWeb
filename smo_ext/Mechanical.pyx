cimport CMath
cimport Math
cimport CMechanical

import numpy as np
cimport numpy as np

cdef class RainflowCounter:
	cdef CMechanical.RainflowCounter* ptr
	def __cinit__(self, int numBins):
		self.ptr = new CMechanical.RainflowCounter(numBins)
	
	def __dealloc__(self):
		del self.ptr
		
	def setStresses(self, double[::1] stressValues not None):
		cdef CMath.MemoryView1D[double]* sView = Math.createMemoryView1D(stressValues)
		self.ptr.setStresses(sView)
		del sView

	def setMeanStressCorrection(self, double M):
		self.ptr.setMeanStressCorrection(M)
	
	def setSNCurveParameters(self, double S_E, double N_E, double k):
		self.ptr.setSNCurveParameters(S_E, N_E, k)
			
	def compute(self):
		return self.ptr.compute()

def computePrincipalStresses(double[:, ::1] stresses not None):
	cdef np.ndarray[double] principalStresses = np.zeros(shape = stresses.shape[0], dtype = np.float)
	cdef CMath.MemoryView2D[double]* sArg = Math.createMemoryView2D(stresses)
	cdef CMath.MemoryView1D[double]* psArg = Math.createMemoryView1D(principalStresses)
	CMechanical.computePrincipalStresses(sArg, psArg)
	del sArg, psArg
	return principalStresses

def computePrincipalStresses_Series(double[:, :, :] stresses not None):
	cdef np.ndarray[double, ndim = 2] principalStresses = np.zeros([stresses.shape[0], 3], dtype = np.float)
	cdef CMath.MemoryView3D[double]* sArg = Math.createMemoryView3D(stresses)
	cdef CMath.MemoryView2D[double]* psArg = Math.createMemoryView2D(principalStresses)
	CMechanical.computePrincipalStresses_Series(sArg, psArg)
	del sArg, psArg
	return principalStresses

def scaleStressSeries_MultiaxialDamage(double[:, :, :] stresses not None, double k):
	cdef CMath.MemoryView3D[double]* sArg = Math.createMemoryView3D(stresses)
	CMechanical.scaleStressSeries_MultiaxialDamage(sArg, k);
	del sArg