import numpy as np
cimport numpy as np
cimport CMath

cdef CMath.MemoryView1D[double]* createMemoryView1D(double [:] a):
	return new CMath.MemoryView1D[double](&a[0], a.shape[0], a.strides[0])

cdef CMath.MemoryView2D[double]* createMemoryView2D(double [:, :] a):
	return new CMath.MemoryView2D[double](&a[0, 0], a.shape[0], a.shape[1], a.strides[0], a.strides[1])

cdef CMath.MemoryView3D[double]* createMemoryView3D(double [:, :, :] a):
	return new CMath.MemoryView3D[double](&a[0, 0, 0], a.shape[0], a.shape[1], a.shape[2], a.strides[0], a.strides[1], a.strides[2])

def testMemoryView2D(double[:, :] data):
	cdef CMath.MemoryView2D[double]* arg = createMemoryView2D(data)
	CMath.testMemoryView2D(arg)
	del arg
	
cdef class Interpolator1D:
	cdef CMath.LinearInterpolator* ptr
	def __cinit__(self, double[:] xData not None, double[:] yData not None):
		cdef CMath.MemoryView1D[double]* x = createMemoryView1D(xData)
		cdef CMath.MemoryView1D[double]* y = createMemoryView1D(yData)
		self.ptr = new CMath.LinearInterpolator(x, y, CMath.ibhLinear)
		del x, y
		
	def __call__(self, double[:] xValues):
		cdef np.ndarray[double] yValues = np.zeros(shape = xValues.shape[0])
		cdef CMath.MemoryView1D[double]* x = createMemoryView1D(xValues)
		cdef CMath.MemoryView1D[double]* y = createMemoryView1D(yValues)
		self.ptr.call(x, y)
		del x, y
		return yValues

cdef class Interpolator2D:
	cdef CMath.BiLinearInterpolator* ptr
	def __cinit__(self, double[:] xData not None, double[:] yData not None, double [:, :] zData not None):
		cdef CMath.MemoryView1D[double]* x = createMemoryView1D(xData)
		cdef CMath.MemoryView1D[double]* y = createMemoryView1D(yData)
		cdef CMath.MemoryView2D[double]* z = createMemoryView2D(zData)
		self.ptr = new CMath.BiLinearInterpolator(x, y, z, CMath.ibhLinear)
		del x, y, z
		
	def __call__(self, double[:] xValues, double[:] yValues):
		cdef np.ndarray[double] zValues = np.zeros(shape = xValues.shape[0])
		cdef CMath.MemoryView1D[double]* x = createMemoryView1D(xValues)
		cdef CMath.MemoryView1D[double]* y = createMemoryView1D(yValues)
		cdef CMath.MemoryView1D[double]* z = createMemoryView1D(zValues)
		self.ptr.call(x, y, z)
		del x, y, z
		return zValues
		