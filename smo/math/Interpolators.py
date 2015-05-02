import numpy as np

class Interpolator2D:
	BOUNDARY_ERROR = 0
	BOUNDARY_CONSTANT = 1
	BOUNDARY_LINEAR = 2
	
	def __init__(self, xData, yData, zData, interp_type = BOUNDARY_LINEAR):
		self.xData = xData
		self.yData = yData
		self.zData = zData
		self.xMin = np.min(self.xData)
		self.xMax = np.max(self.xData)
		self.yMin = np.min(self.yData)
		self.yMax = np.max(self.yData)
		
		if (interp_type == self.BOUNDARY_ERROR):
			self.fInterpFunction = self.__interpFunction_BoundaryError
		elif (interp_type == self.BOUNDARY_CONSTANT):
			self.fInterpFunction = self.__interpFunction_BoundaryConstant
		elif (interp_type == self.BOUNDARY_LINEAR):
			self.fInterpFunction =  self.__interpFunction_BoundaryLinear
		else:
			raise ValueError("Invalid value '%d' for the interpolation type. The valid value are " 
				"{0-BOUNDARY_ERROR, 1-BOUNDARY_CONSTANT, 2-BOUNDARY_LINEAR}."%(interp_type))
		
	def __call__(self, xIn, yIn):		
		return map(self.fInterpFunction, xIn, yIn)
		
	def __interpFunction_BoundaryError(self, x, y):
		if (x < self.xMin or x > self.xMax or y < self.yMin or y > self.yMax):
			raise ValueError("Input data (%e, %e) out of the interpolator range"%(x, y))
		
		xNextIndex = np.searchsorted(self.xData, x)		
		if (xNextIndex == 0):
			xPrevIndex = 0
			xCoeff = 0
		else:
			xPrevIndex = xNextIndex-1
			xCoeff = (x-self.xData[xPrevIndex])/(self.xData[xNextIndex]-self.xData[xPrevIndex])
		
		yNextIndex = np.searchsorted(self.yData, y)
		if (yNextIndex == 0):
			yPrevIndex = 0
			yCoeff = 0
		else:
			yPrevIndex = yNextIndex-1
			yCoeff = (y-self.yData[yPrevIndex])/(self.yData[yNextIndex]-self.yData[yPrevIndex])
		
		value1 = self.zData[yPrevIndex][xPrevIndex] + xCoeff*(self.zData[yPrevIndex][xNextIndex]-self.zData[yPrevIndex][xPrevIndex])
		value2 = self.zData[yNextIndex][xPrevIndex] + xCoeff*(self.zData[yNextIndex][xNextIndex]-self.zData[yNextIndex][xPrevIndex])
		interpValue = value1 + yCoeff*(value2 - value1)
		return interpValue 	

	def __interpFunction_BoundaryLinear(self, x, y):	
		xNextIndex = np.searchsorted(self.xData, x)	
		if (xNextIndex == 0):
			xPrevIndex = 0
			xNextIndex = 1
		elif (xNextIndex >= len(self.xData)):
			xNextIndex = xNextIndex - 1
			xPrevIndex = xNextIndex - 1
		else:
			xPrevIndex = xNextIndex-1
		xCoeff = (x-self.xData[xPrevIndex])/(self.xData[xNextIndex]-self.xData[xPrevIndex])
		
		yNextIndex = np.searchsorted(self.yData, y)
		if (yNextIndex == 0):
			yPrevIndex = 0
			yNextIndex = 1
		elif (yNextIndex >= len(self.yData)):
			yNextIndex = yNextIndex - 1
			yPrevIndex = yNextIndex - 1
		else:
			yPrevIndex = yNextIndex-1
		yCoeff = (y-self.yData[yPrevIndex])/(self.yData[yNextIndex]-self.yData[yPrevIndex])
		
		value1 = self.zData[yPrevIndex][xPrevIndex] + xCoeff*(self.zData[yPrevIndex][xNextIndex]-self.zData[yPrevIndex][xPrevIndex])
		value2 = self.zData[yNextIndex][xPrevIndex] + xCoeff*(self.zData[yNextIndex][xNextIndex]-self.zData[yNextIndex][xPrevIndex])
		interpValue = value1 + yCoeff*(value2 - value1)
		return interpValue
	
	def __interpFunction_BoundaryConstant(self, x, y):
		xNextIndex = np.searchsorted(self.xData, x)	
		if (xNextIndex == 0):
			xNextIndex = 0
			xPrevIndex = xNextIndex
			xCoeff = 0
		elif (xNextIndex >= len(self.xData)):
			xNextIndex = xNextIndex - 1
			xPrevIndex = xNextIndex
			xCoeff = 0
		else:
			xPrevIndex = xNextIndex-1
			xCoeff = (x-self.xData[xPrevIndex])/(self.xData[xNextIndex]-self.xData[xPrevIndex])
		
		yNextIndex = np.searchsorted(self.yData, y)
		if (yNextIndex == 0):
			yNextIndex = 0
			yPrevIndex = yNextIndex
			yCoeff = 0
		elif (yNextIndex >= len(self.yData)):
			yNextIndex = yNextIndex - 1
			yPrevIndex = yNextIndex
			yCoeff = 0
		else:
			yPrevIndex = yNextIndex-1
			yCoeff = (y-self.yData[yPrevIndex])/(self.yData[yNextIndex]-self.yData[yPrevIndex])
		
		value1 = self.zData[yPrevIndex][xPrevIndex] + xCoeff*(self.zData[yPrevIndex][xNextIndex]-self.zData[yPrevIndex][xPrevIndex])
		value2 = self.zData[yNextIndex][xPrevIndex] + xCoeff*(self.zData[yNextIndex][xNextIndex]-self.zData[yNextIndex][xPrevIndex])
		interpValue = value1 + yCoeff*(value2 - value1)
		return interpValue

	@staticmethod
	def test():
		x = np.array([0, 1, 2])
		y = np.array([0, 1, 2])
		z = np.array([
			[2, 3, 4], 
			[3, 4, 5], 
	  		[4, 5, 6]
		  ])
		interp = Interpolator2D(x, y, z)
		print interp([0.5], [0.5])
		
def testInterpolator2D_SmoVsScipy():	
	# Define interpolator values
	x = np.arange(-2.0, 3.0, 1)
	y = np.arange(-2.0, 3.0, 1)
	print "x = ", x
	print "y = ", y
	xx, yy = np.meshgrid(x, y)
	#z = np.sin(xx**2 + yy**2 + xx**3)
	z = xx + yy
	
	# Define (x,y) values for checking
	xNew = np.arange(-3., 3.5, 0.5)
	yNew = np.arange(-3., 3.5, 0.5)
	
	# Interpolate with scipy.interp2d
	from scipy import interpolate
	fInterpScipy = interpolate.interp2d(x, y, z, kind='linear', bounds_error = False, fill_value = None)
	zNewScipy = fInterpScipy(xNew, yNew)
	
	# Interpolate with SmoPy.Interpolator2D
	fInterpSmoPy = Interpolator2D(x, y, z, interp_type = Interpolator2D.BOUNDARY_LINEAR)	
	zNewSmoPy = np.zeros(shape = (len(xNew), len(yNew)))
	for i in range(len(xNew)):
		for j in range(len(yNew)):
			zNewSmoPy[j][i] = fInterpSmoPy(np.array([xNew[i]]), np.array([yNew[j]]))[0]
	
	# Interpolate with SmoC.Interpolator2D
	from compiled.Damage_Compiled import Interpolator2D as I2D
	fInterpSmoC = I2D(x, y, z)
	zNewSmoC = np.zeros(shape = (len(xNew), len(yNew)))
	for i in range(len(xNew)):
		for j in range(len(yNew)):
			zNewSmoC[j][i] = fInterpSmoC(np.array([xNew[i]]), np.array([yNew[j]]))[0]
	
	# Compare interpolators
	#testCompareInterpolators(xNew, yNew, 'scipy.interp2d', zNewScipy, 'SmoPy.Interpolator2D', zNewSmoPy)
	#testCompareInterpolators(xNew, yNew, 'scipy.interp2d', zNewScipy, 'SmoC.Interpolator2D', zNewSmoC)
	testCompareInterpolators(xNew, yNew, 'SmoPy.Interpolator2D', zNewSmoPy, 'SmoC.Interpolator2D', zNewSmoC)
	
def testCompareInterpolators(xNew, yNew, interp1Name, z1, interp2Name, z2):
	print "\n"
	print "xNew = ", xNew
	print "yNew = ", yNew
	print "\n%s(x,y) = \n"%interp1Name, z1
	print "\n%s(x,y) = \n"%interp2Name, z2
	
	# Check for differents between interpolators
	errFileName = 'TestInterpolator2D_Errors.txt'
	errFile = open(errFileName, 'w')
	hasErrors = False
	zErr = z1 - z2
	for i in range(len(xNew)):
		for j in range(len(yNew)):
			if abs(zErr[i][j]) > 1e-9:
				if hasErrors == False:
					hasErrors = True
					errFile.write("FAILED: %s is NOT the same as %s\n"%(interp1Name, interp2Name))
				errFile.write("@see: (x,y)=(%f,%f) with error = %g\n"%(xNew[i],yNew[j], zErr[i][j]))
	errFile.close()
	
	if hasErrors == False:
		print "\nOK: %s is the same as %s"%(interp1Name, interp2Name)
	else:
		print "\nFAILED: %s is NOT the same as %s\n@see: '%s'"%(interp1Name, interp2Name, errFileName)
		
	

if __name__ == '__main__':
	#Interpolator2D.test()		
	testInterpolator2D_SmoVsScipy()
	