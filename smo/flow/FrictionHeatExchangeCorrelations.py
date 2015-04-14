'''
Created on Apr 14, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import math as m

def Nusselt_StraightPipe_Laminar(Re, Pr):
	# @see VDI Heat Atlas, page 693, Eq. (1)
	return 3.66

def Nusselt_StraightPipe_Turbulent(Re, Pr):
	# Friction factor - @see VDI Heat Atlas, page 696, Eq. (26) and (27)
	# Range of validity: 1e4 < Re < 1e6, 0.1 < Pr < 1000
	# Limit the Prandtl number, to prevent crashing around the critical point
	# m::limitVariable(Pr, 0, 100);
	xi = m.pow(1.8 * m.log10(Re) - 1.5, -2);
	NuNum = (xi / 8) * Re * Pr;
	NuDenom = 1 + 12.7 * m.sqrt(xi / 8) * (m.pow(Pr, 2./3) - 1);
	return NuNum/NuDenom;
	
def Nusselt_StraightPipe(Re, Pr):
	ReL = 2300.; #see VDI Heat Atlas, page 696, Sect. 4.2
	ReH = 1e4;
	if (Re < ReL):
		#VDI Heat Atlas, page 693, Eq. (1)
		Nu = Nusselt_StraightPipe_Laminar(Re, Pr)
	elif (Re > ReH):
		Nu = Nusselt_StraightPipe_Turbulent(Re, Pr)
	else:
		# Interpolation coefficient
		gamma = (Re - ReL) / (ReH - ReL);
		Nu = (1 - gamma) * Nusselt_StraightPipe_Laminar(ReL, Pr) + gamma * Nusselt_StraightPipe_Turbulent(ReH, Pr);
	return Nu;

def ChurchilCorrelation(Re, d, epsilon):
	theta1 = m.pow(2.457 * m.log(m.pow(7.0 / Re, 0.9) + 0.27 * epsilon / d), 16)
	theta2 = m.pow(37530.0 / Re, 16)
	zeta = 8 * m.pow(m.pow((8.0 / Re), 12) + 1 / m.pow((theta1 + theta2), 1.5) , 1./12)
	return zeta