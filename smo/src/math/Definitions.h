#ifndef MATHDEFINITIONS_H_
#define MATHDEFINITIONS_H_

#include <cmath>

inline double Max(const double& a, const double& b) {
	return b > a ? b : a;
}

inline double Min(const double& a, const double& b) {
	return b < a ? b : a;
}

inline bool isNaN(double value) {
	return std::isnan(value);
}


#define ShowMessage(message) \
	std::stringstream messageStream; \
	messageStream << "\n" << message; \
	std::string messageString(messageStream.str()); \
	SimulationEnvironment_message(messageString.c_str());

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
	throw -1; \
	} \

#define RaiseWarning(message) \
	{ \
	_RaiseEvent(message) \
	} \

#endif //MATHDEFINITIONS_H_
