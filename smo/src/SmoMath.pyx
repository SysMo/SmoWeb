import cython
import numpy as np
cimport numpy as np

cimport SmoMathImports as _SmoMath

#ctypedef np.ndarray[double, ndim=1, mode="c"] VectorD

cdef class LinearInterpolator:
	cdef _SmoMath.LinearInterpolator* ptr
	def __cinit__(self, double[::1] xValues not None, double[::1] yValues not None):
		cdef int numValues = xValues.shape[0]
		cdef double* x = &xValues[0]
		cdef double* y = &yValues[0]
		self.ptr = new _SmoMath.LinearInterpolator(x, y, numValues, False, _SmoMath.ibhConstant)
	
	def __call__(self, double x):
		return self.ptr.call(x)
	
	def __dealloc__(self):
		del self.ptr