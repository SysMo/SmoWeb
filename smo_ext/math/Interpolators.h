/*
 * Interpolators.h
 *
 *  Created on: Aug 7, 2013
 *      Author: Atanas Pavlov
 *	 Copyright: SysMo Ltd., Bulgaria
 */

#ifndef INTERPOLATORS_H_
#define INTERPOLATORS_H_

#include "core/Definitions.h"
#include "ArrayInterface.h"
#include "VectorsMatrices.h"



/**
 * InterpalatorBase
 */
class InterpolatorBase {
public:
	enum BoundaryHandling {
		ibhError = 0,
		ibhConstant = 1,
		ibhLinear = 2
	};
};



/**
 * GridInterpolator
 */
class GridInterpolator : public InterpolatorBase {
public:
	static int hunt(double* valueArray, int numValues, double xValue, int interpolationOrder);
};



/**
 * Interpolator1D
 */
class Interpolator1D : public GridInterpolator {
public:
	Interpolator1D(
			MemoryView1D<double>* xValues,
			MemoryView1D<double>* yValues,
			int interpolationOrder,
			BoundaryHandling boundaryHandling = ibhConstant);
	virtual ~Interpolator1D();
	virtual double operator()(double value);
	virtual void operator()(MemoryView1D<double>* inValues, MemoryView1D<double>* outValues);

protected:
	virtual double rawInterp(int xIndex, double value) = 0;

	double* xValues;
	double* yValues;

	int numValues;
	int interpolationOrder;
	BoundaryHandling boundaryHandling;
};



/**
 * LinearInterpolator
 */
class LinearInterpolator : public Interpolator1D {
public:
	LinearInterpolator(
			MemoryView1D<double>* xValues,
			MemoryView1D<double>* yValues,
			BoundaryHandling boundaryHandling = ibhConstant);

protected:
	virtual double rawInterp(int xIndex, double xValue);
};



/**
 * Interpolator2D
 */
class Interpolator2D : public GridInterpolator {
public:
	Interpolator2D(
			MemoryView1D<double>* xValues,
			MemoryView1D<double>* yValues,
			MemoryView2D<double>* zValues,
			int interpolationOrder,
			BoundaryHandling boundaryHandling = ibhConstant);
	virtual ~Interpolator2D();
	virtual double operator()(double xValue, double yValue);
	virtual void operator()(
			MemoryView1D<double>* inXValues,
			MemoryView1D<double>* inYValues,
			MemoryView1D<double>* outZValues);

protected:
	virtual double rawInterp(int xIndex, double xValue, int yIndex, double yValue) = 0;

	double* xValues;
	double* yValues;
	NRmatrix<double> zValues;

	int numXValues;
	int numYValues;
	int interpolationOrder;
	BoundaryHandling boundaryHandling;
};



/**
 * BiLinearInterpolator
 */
class BiLinearInterpolator : public Interpolator2D {
public:
	BiLinearInterpolator(
			MemoryView1D<double>* xValues,
			MemoryView1D<double>* yValues,
			MemoryView2D<double>* zValues,
			BoundaryHandling boundaryHandling = ibhConstant);

protected:
	virtual double rawInterp(int xIndex, double xValue, int yIndex, double yValue);
};

#endif /* INTERPOLATORS_H_ */
