from Media import Medium, MediumState
import numpy as np

f1 = Medium.create(Medium.sCompressibleFluidCoolProp, 'ParaHydrogen', 1)
s1 = MediumState(f1)
s1.update_ph(6.9176e+07, 1.0052e+06);
#s1.update_ph(6.9176e+07, 20520.8);
print s1.T() - 273.15

# for T in np.linspace(-1, 110, 200):
# 	p1 = MediumState(f1)
# 	p1.update_Tp(T + 273.15, 1e5)
# 	print ("T = %f, rho = %f"%(T, p1.rho()))
# 	#print p1.cond()