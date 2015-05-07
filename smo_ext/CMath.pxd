cimport numpy as np

cdef extern from "math/ArrayInterface.h":
	cdef cppclass MemoryView1D[T]:
		MemoryView1D(T* data, ssize_t dim1, ssize_t stride1)
	cdef cppclass MemoryView2D[T]:
		MemoryView2D(T* data, ssize_t dim1, ssize_t dim2, ssize_t stride1, ssize_t stride2)
	cdef cppclass MemoryView3D[T]:
		MemoryView3D(T* data, ssize_t dim1, ssize_t dim2, ssize_t dim3, ssize_t stride1, ssize_t stride2, ssize_t stride3)
	void testMemoryView2D(MemoryView2D[double]* view) except +

cdef extern from "math/Interpolators.h":
	cdef enum BoundaryHandling "InterpolatorBase::BoundaryHandling":
		ibhError "InterpolatorBase::ibhError"
		ibhConstant "InterpolatorBase::ibhConstant"
		ibhLinear "InterpolatorBase::ibhLinear"

	cdef cppclass LinearInterpolator:
		LinearInterpolator(MemoryView1D[double]* xValues, MemoryView1D[double]* yValues,
				BoundaryHandling boundaryHandling) except +
		double call 'operator()' (double value) except +
		void call 'operator()' (MemoryView1D[double]* inValues, MemoryView1D[double]* outValues) except +
		
	cdef cppclass BiLinearInterpolator:
		BiLinearInterpolator(MemoryView1D[double]* xValues, MemoryView1D[double]* yValues,
				MemoryView2D[double]* zValues, BoundaryHandling boundaryHandling) except +
		double call 'operator()' (double xValue, double yValue) except +
		void call 'operator()' (MemoryView1D[double]* inXValues, MemoryView1D[double]* inYValues, MemoryView1D[double]* outZValues) except +
