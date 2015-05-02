import numpy as np
import smo_ext.Math as Math

def printArrayInfo(z):
	print ("Shape: {}; Strides: {}; Type: {}".format(z.shape, z.strides, type(z)))
	print

x = np.arange(9, dtype = np.float)
y = np.arange(12, dtype = np.float)

xx, yy = np.meshgrid(x, y)

zz = 100 * xx + yy
print ("Python/NumPy")
print ("Data:")
print(zz)
print
printArrayInfo(zz)

print ("Transpose")
zColumn = zz.T
zColumn[3, 5] = 123.
print zColumn[3, 5]
print zz[5, 3]
print(zColumn)
printArrayInfo(zColumn)

print ("Bool select")
zBoolSel = zz[zz > 300]
printArrayInfo(zBoolSel)

Math.testMemoryView2D(zz)
print
Math.testMemoryView2D(zColumn)
