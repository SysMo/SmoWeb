/*
 * Interpolators.h
 *
 *  Created on: Aug 7, 2013
 *      Author: Atanas Pavlov
 *	 Copyright: SysMo Ltd., Bulgaria
 */

#ifndef INTERPOLATORS_H_
#define INTERPOLATORS_H_

#include "Definitions.h"
#include "VectorsMatrices.h"

enum InterpolationBoundaryHandling {
	ibhConstant = 0,
	ibhConstantSlope = 1
};

class Interpolator1D {

public:
	Interpolator1D(VectorD& xValues, VectorD& yValues, size_t interpolationOrder,
			bool copyValues = true, InterpolationBoundaryHandling boundaryHandling = ibhConstant);
	Interpolator1D(double* xValues, double* yValues, int numValues, size_t interpolationOrder,
			bool copyValues = true,	InterpolationBoundaryHandling boundaryHandling = ibhConstant);

	virtual ~Interpolator1D();
	virtual double operator()(double value);
protected:
	size_t hunt(double xValue);
	virtual double rawInterp(size_t xIndex, double value) = 0;

	bool keepValues;
	double* xValues;
	double* yValues;

	size_t numValues;
	size_t interpolationOrder;
	InterpolationBoundaryHandling boundaryHandling;

};

class LinearInterpolator : public Interpolator1D {
public:
	LinearInterpolator(VectorD& xValues, VectorD& yValues, bool copyValues = true,
			InterpolationBoundaryHandling boundaryHandling = ibhConstant)
	: Interpolator1D(xValues, yValues, 2, copyValues, boundaryHandling){};
	LinearInterpolator(double* xValues, double* yValues, int numValues, bool copyValues = true,
			InterpolationBoundaryHandling boundaryHandling = ibhConstant)
	: Interpolator1D(xValues, yValues, numValues, 2, copyValues, boundaryHandling){};
	double rawInterp(size_t xIndex, double xValue);
};



#endif /* INTERPOLATORS_H_ */
