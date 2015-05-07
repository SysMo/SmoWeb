#ifndef MATHDEFINITIONS_H_
#define MATHDEFINITIONS_H_

//#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <math.h>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <stdio.h>
#include <iostream>

#ifdef _MSC_VER
#include <float.h>
#include <pyconfig.h>
#else
#include <python2.7/pyconfig.h>
#endif //_MSC_VER

inline double Max(const double& a, const double& b) {
	return b > a ? b : a;
}

inline int Max(const int& a, const int& b) {
	return b > a ? b : a;
}
inline double Min(const double& a, const double& b) {
	return b < a ? b : a;
}

inline int Min(const int& a, const int& b) {
	return b < a ? b : a;
}

inline int isNaN(double value) {
#ifdef _MSC_VER
	return _isnan(value);
#else
	return isnan(value);
#endif //_MSC_VER
}

const double Infinity  = std::numeric_limits<double>::infinity();
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif


//#ifdef _MSC_VER
//
//#include <BaseTsd.h>
//typedef SSIZE_T ssize_t;
//
//#endif //_MSC_VER

#define ShowMessage(message) {\
	std::stringstream messageStream; \
	messageStream << "\n" << message; \
	std::string messageString(messageStream.str()); \
	std::cout << messageString; \
	} \

#define _RaiseEvent(message) \
	std::stringstream messageStream; \
	messageStream << "\n" << \
	"--------------------------------------------------\n" << \
	"--------------------------------------------------\n" << \
	"Event: " << message << "\n" << \
	"File: " << __FILE__ << "\n" << \
	"Function: " << __FUNCTION__ << "\n" << \
	"Line: " << __LINE__ << "\n" << \
	"--------------------------------------------------\n"; \
	std::string messageString(messageStream.str()); \

#define RaiseError(message) \
	{ \
	_RaiseEvent(message) \
	throw std::runtime_error(messageString.c_str()); \
	} \

#define RaiseWarning(message) \
	{ \
	_RaiseEvent(message) \
	} \

#endif //MATHDEFINITIONS_H_
