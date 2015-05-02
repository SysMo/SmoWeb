/*
 * Interpolators.cpp
 *
 *  Created on: Aug 7, 2013
 *      Author: Atanas Pavlov
 *	 Copyright: SysMo Ltd., Bulgaria
 */

#include "Interpolators.h"

/**
 * GridInterpolator
 */
int GridInterpolator::hunt(double* valueArray, int numValues, double xValue, int interpolationOrder) {
	int jm, ju, inc = 1;
	int jl = 0;
	if (numValues < 2 || interpolationOrder < 2 || interpolationOrder > numValues)
		throw("hunt size error");

	if (xValue >= valueArray[jl]) {
		for (;;) {
			ju = jl + inc;
			if (ju >= numValues - 1) {
				ju = numValues - 1;
				break;
			} else if (xValue < valueArray[ju])
				break;
			else {
				jl = ju;
				inc += inc;
			}
		}
	} else {
		ju = jl;
		for (;;) {
			jl = jl - inc;
			if (jl <= 0) {
				jl = 0;
				break;
			} else if (xValue >= valueArray[jl])
				break;
			else {
				ju = jl;
				inc += inc;
			}
		}
	}
	while (ju - jl > 1) {
		jm = (ju + jl) >> 1;
		if (xValue >= valueArray[jm])
			jl = jm;
		else
			ju = jm;
	}

	return Max(0, Min(numValues - interpolationOrder, jl - ((interpolationOrder - 2) >> 1)));
}



/**
 * Interpolator1D
 */
Interpolator1D::Interpolator1D(
		MemoryView1D<double>* xValues,
		MemoryView1D<double>* yValues,
		int interpolationOrder,
		BoundaryHandling boundaryHandling) :
		interpolationOrder(interpolationOrder),
		boundaryHandling(boundaryHandling) {
	this->numValues = xValues->len();
	this->xValues = new double[numValues];
	this->yValues = new double[numValues];
	xValues->copyTo(this->xValues);
	yValues->copyTo(this->yValues);
}

Interpolator1D::~Interpolator1D() {
	delete[] xValues;
	delete[] yValues;
}

double Interpolator1D::operator()(double value) {
	if (isNaN(value)) {
		RaiseError("Not-a-number value passesd to interpolator");
	}

	double yValue;
	if (value < xValues[0] && boundaryHandling == ibhConstant) {
			yValue = yValues[0];
	} else if (value > xValues[numValues - 1] && boundaryHandling == ibhConstant) {
			yValue = yValues[numValues - 1];
	} else {
		int i = hunt(xValues, numValues, value, interpolationOrder);
		yValue = rawInterp(i, value);
	}

	return yValue;
}

void Interpolator1D::operator()(MemoryView1D<double>* inValues, MemoryView1D<double>* outValues) {
	for (int i = 0; i < inValues->len(); i++) {
		(*outValues)(i) = (*this)((*inValues)(i));
	}
}



/**
 * LinearInterpolator
 */
LinearInterpolator::LinearInterpolator(
		MemoryView1D<double>* xValues,
		MemoryView1D<double>* yValues,
		BoundaryHandling boundaryHandling) :
		Interpolator1D(xValues, yValues, 2, boundaryHandling) {
}

double LinearInterpolator::rawInterp(int xIndex, double xValue) {
	if (xValues[xIndex] == xValues[xIndex + 1]) {
		return yValues[xIndex];
	} else {
		return yValues[xIndex] + ((xValue - xValues[xIndex])
				/ (xValues[xIndex + 1] - xValues[xIndex]))
				* (yValues[xIndex + 1] - yValues[xIndex]);
	}
}



/**
 * Interpolator2D
 */
Interpolator2D::Interpolator2D(
		MemoryView1D<double>* xValues,
		MemoryView1D<double>* yValues,
		MemoryView2D<double>* zValues,
		int interpolationOrder,
		BoundaryHandling boundaryHandling) :
		zValues(zValues),
		interpolationOrder(interpolationOrder),
		boundaryHandling(boundaryHandling) {
	numXValues = xValues->len();
	numYValues = yValues->len();
	if (numXValues != zValues->shape(1)) {
		RaiseError("Inconsistent input data, the length of xValues("<< numXValues << ") must be equal to the number of columns of zValues ("<< zValues->shape(1) << ")")
	}
	if (numYValues != zValues->shape(0)) {
		RaiseError("Inconsistent input data, the length of yValues("<< numYValues << ") must be equal to the number of rows of zValues("<< zValues->shape(0) << ")")
	}
	this->xValues = new double[numXValues];
	this->yValues = new double[numYValues];
	xValues->copyTo(this->xValues);
	yValues->copyTo(this->yValues);
}

Interpolator2D::~Interpolator2D() {
	delete[] xValues;
	delete[] yValues;
}

double Interpolator2D::operator()(double xValue, double yValue) {
	if (isNaN(xValue) || isNaN(yValue)) {
		RaiseError("Not-a-number value passed to interpolator");
	}

	if (boundaryHandling == ibhError) {
		if (xValue < xValues[0] || xValues[numXValues - 1] < xValue
				|| yValue < yValues[0] || yValues[numYValues - 1] < yValue) {
			RaiseError("Input data (" << xValue << ", " << yValue <<") out of the interpolator range.");
		}

		int iX = hunt(xValues, numXValues, xValue, interpolationOrder);
		int iY = hunt(yValues, numYValues, yValue, interpolationOrder);
		double zValue = rawInterp(iX, xValue, iY, yValue);
		return zValue;

	} else if (boundaryHandling == ibhConstant) {
		int iX = -1;
		if (xValue < xValues[0]) {
			iX = 0;
			xValue = xValues[iX];
		} else if (xValue > xValues[numXValues - 1]) {
			iX = numXValues -1;
			xValue = xValues[iX];
			iX -= 1;
		}

		int iY = -1;
		if (yValue < yValues[0]) {
			iY = 0;
			yValue = yValues[iY];
		} else if (yValue > yValues[numYValues - 1]) {
			iY = numYValues -1;
			yValue = yValues[iY];
			iY -= 1;
		}

		if (iX == -1) {
			iX = hunt(xValues, numXValues, xValue, interpolationOrder);
		}
		if (iY == -1) {
			iY = hunt(yValues, numYValues, yValue, interpolationOrder);
		}

		double zValue = rawInterp(iX, xValue, iY, yValue);
		return zValue;

	} else if (boundaryHandling == ibhLinear) {
		int iX = hunt(xValues, numXValues, xValue, interpolationOrder);
		int iY = hunt(yValues, numYValues, yValue, interpolationOrder);

		double zValue = rawInterp(iX, xValue, iY, yValue);
		return zValue;

	} else {
		RaiseError("Unsuported type of the BoundaryHandling.");
		return 0.0;
	}
}

void Interpolator2D::operator()(MemoryView1D<double>* inXValues, MemoryView1D<double>* inYValues, MemoryView1D<double>* outZValues) {
	for (int i = 0; i < inXValues->len(); i++) {
		(*outZValues)(i) = (*this)((*inXValues)(i), (*inYValues)(i));
	}
}



/**
 * BiLinearInterpolator
 */
BiLinearInterpolator::BiLinearInterpolator(
		MemoryView1D<double>* xValues,
		MemoryView1D<double>* yValues,
		MemoryView2D<double>* zValues,
		BoundaryHandling boundaryHandling) :
		Interpolator2D(xValues, yValues, zValues, 2, boundaryHandling) {
}

double BiLinearInterpolator::rawInterp(int xIndex, double xValue, int yIndex, double yValue) {
	double t = (xValue - xValues[xIndex])/(xValues[xIndex + 1] - xValues[xIndex]);
	double u = (yValue - yValues[yIndex])/(yValues[yIndex + 1] - yValues[yIndex]);
	double zValue = (1. - t) * (1. - u) * zValues[yIndex][xIndex] + t * (1. - u) * zValues[yIndex][xIndex + 1]
		+ (1. - t) * u * zValues[yIndex + 1][xIndex] + t * u * zValues[yIndex + 1][xIndex + 1];
	return zValue;
}

