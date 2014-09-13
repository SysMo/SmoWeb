from Media import Medium, MediumState
import numpy as np

f1 = Medium.create(Medium.sCompressibleFluidCoolProp, 'Water', 1)

for T in np.linspace(-1, 110, 200):
	p1 = MediumState(f1)
	p1.update_Tp(T + 273.15, 1e5)
	print ("T = %f, rho = %f"%(T, p1.rho()))
	#print p1.cond()