from libcpp cimport bool

cdef extern from "math/Interpolators.h":
	cdef enum InterpolationBoundaryHandling:
		ibhConstant = 0
		ibhConstantSlope = 1
	cdef cppclass LinearInterpolator:
		LinearInterpolator(double* xValues, double* yValues, int numValues, bool copyValues,
				InterpolationBoundaryHandling boundaryHandling)
		double call 'operator()' (double value)