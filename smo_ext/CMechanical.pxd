from CMath cimport *

cdef extern from "mechanical/RainflowCounter.h":
	cdef cppclass RainflowCounter:
		RainflowCounter(int numBins)
		void setStresses(MemoryView1D[double]* sValues) except +
		void setMeanStressCorrection(double M)
		void setSNCurveParameters(double S_E, double N_E, double k)
		double compute() except +

cdef extern from "mechanical/StressTensorCalculator.h" namespace "StressTensorCalculator":
	void computePrincipalStresses(MemoryView2D[double]* stresses, MemoryView1D[double]* principalStresses) except +
	void computePrincipalStresses_Series(MemoryView3D[double]* stressSeries, MemoryView2D[double]* principalStresses) except +
	void scaleStressSeries_MultiaxialDamage(MemoryView3D[double]* stressSeries, double k) except +