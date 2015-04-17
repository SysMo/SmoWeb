'''
Created on Apr 14, 2015

@author:  Atanas Pavlov
@copyright: SysMo Ltd, Bulgaria
'''
import math as m

def Nusselt_StraightPipe_Laminar(Re, Pr):
	#@see VDI Heat Atlas, page 693, Eq. (1)
	return 3.66

def Nusselt_StraightPipe_Turbulent(Re, Pr):
	"""
	@param Re Reynolds number
	@param Pr Prandtl number
	"""
	# Friction factor - @see VDI Heat Atlas, page 696, Eq. (26) and (27)
	# Range of validity: 1e4 < Re < 1e6, 0.1 < Pr < 1000
	# Limit the Prandtl number, to prevent crashing around the critical point
	# m::limitVariable(Pr, 0, 100);
	xi = m.pow(1.8 * m.log10(Re) - 1.5, -2);
	NuNum = (xi / 8) * Re * Pr;
	NuDenom = 1 + 12.7 * m.sqrt(xi / 8.) * (m.pow(Pr, 2./3) - 1);
	return NuNum/NuDenom;
	
def Nusselt_StraightPipe(Re, Pr):
	"""
	@param Re Reynolds number
	@param Pr Prandtl number
	"""
	ReL = 2300.; #@see VDI Heat Atlas, page 696, Sect. 4.2
	ReH = 1e4;
	if (Re < ReL):
		#@see VDI Heat Atlas, page 693, Eq. (1)
		Nu = Nusselt_StraightPipe_Laminar(Re, Pr)
	elif (Re > ReH):
		Nu = Nusselt_StraightPipe_Turbulent(Re, Pr)
	else:
		# Interpolation coefficient
		gamma = (Re - ReL) / (ReH - ReL);
		Nu = (1 - gamma) * Nusselt_StraightPipe_Laminar(ReL, Pr) + gamma * Nusselt_StraightPipe_Turbulent(ReH, Pr);
	return Nu;

def ChurchilCorrelation(Re, d, epsilon):
	"""
	@param: Re Reynolds number
    @param: d hydraulic diameter
    @param: epsilon surface Roughness
	"""
	# "Churchill'1977" equation for friction factor in the laminar, transition and turbulent flow
	# @see: http://en.wikipedia.org/wiki/Darcy_friction_factor_formulae#Table_of_Approximations)
	# @see: AMESim help for 'tpf_pipe_fr' function
	theta1 = m.pow(2.457 * m.log(m.pow(7.0 / Re, 0.9) + 0.27 * epsilon / d), 16.)
	theta2 = m.pow(37530.0 / Re, 16.)
	zeta = 8 * m.pow(m.pow((8.0 / Re), 12.) + 1 / m.pow((theta1 + theta2), 1.5), 1./12)
	return zeta

def Nusselt_HelicalChannel_Laminar(Re, Pr, d_D):
	"""
	@param Re Reynolds number
	@param Pr Prandtl number
	@param d_D (hydraulic diameter) / (average curvature diameter)
	"""
	#@see VDI Heat Atlas, page 710, Eq. (12)
	m = 0.5 + 0.2903 * m.pow(d_D, 0.194);
	Nu = 3.66 + 0.08 * (1 + 0.8 * m.pow(d_D, 0.9)) * m.pow(Re, m) * m.pow (Pr, 1/3.)
	return Nu

def Nusselt_HelicalChannel_Turbulent(Re, Pr, d_D):
	"""
	@param Re Reynolds number
	@param Pr Prandtl number
	@param d_D (hydraulic diameter) / (average curvature diameter)
	"""
	#@see VDI Heat Atlas, page 710, Eq. (14)
	xi = 0.3164 / m.pow(Re, 0.25) + 0.03 * m.pow(d_D, 0.5)
	#@see VDI Heat Atlas, page 710, Eq. (13)				
	NuNum = (xi / 8) * Re * Pr;
	NuDenom = 1 + 12.7 * m.sqrt(xi / 8.) * (m.pow(Pr, 2./3) - 1);
	return NuNum/NuDenom;
	
def Nusselt_HelicalChannel(Re, Pr, d_D):
	"""
	@param Re Reynolds number
	@param Pr Prandtl number
	@param d_D (hydraulic diameter) / (average curvature diameter)
	"""
	#@see VDI Heat Atlas, page 709, Eq. (4)
	ReL = 2300.* (1 + 8.6 * pow(d_D, 0.45))
	ReH = 2.2e4
	if (Re < ReL):
		#@see VDI Heat Atlas, page 693, Eq. (1)
		Nu = Nusselt_HelicalChannel_Laminar(Re, Pr, d_D)
	elif (Re > ReH):
		Nu = Nusselt_HelicalChannel_Turbulent(Re, Pr, d_D)
	else:
		# Interpolation coefficient
		gamma = (Re - ReL) / (ReH - ReL);
		Nu = (1 - gamma) * Nusselt_HelicalChannel_Laminar(ReL, Pr, d_D)\
			 + gamma * Nusselt_HelicalChannel_Turbulent(ReH, Pr, d_D);
	return Nu;

def frictionFactor_HelicalChannel(Re, d_D):
	"""
	@param Re Reynolds number
	@param d_D (hydraulic diameter) / (average curvature diameter)
	"""
	#@see VDI Heat Atlas, page 1062, Eq. (12)
	zeta = 0.3164 / m.pow(Re, 0.25) \
			+ 0.03 * m.pow(d_D, 0.5);
	# This is in turbulent, what about laminar?
	return zeta
