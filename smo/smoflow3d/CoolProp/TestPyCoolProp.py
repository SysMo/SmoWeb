from smo.smoflow3d.CoolProp.CoolProp import Fluid, FluidState

def testFluid():
	#f = Fluid('R134a')
	f = Fluid('ParaHydrogen')
	#f = Fluid('Water')
	BibTexKeys = ["EOS", "CP0", "VISCOSITY", "CONDUCTIVITY",
						 "ECS_LENNARD_JONES", "ECS_FITS", "SURFACE_TENSION"]
	for key in BibTexKeys:
		print("{0} : {1}".format(key, f.BibTeXKey(key)))
	
	print("{0} : {1}".format('EOS reference', f.EOSReference()))
	print("{0} : {1}".format('Transpor reference', f.TransportReference()))
		
	print("{0} : {1} [g/mol]".format('Molar mass', f.molarMass()))
	print("{0} : {1}".format('Accentric factor', f.accentricFactor()))
	print("{0} : {1}".format('Critical point', f.critical()))
	print("{0} : {1}".format('Tripple point', f.tripple()))
	print("{0} : {1}".format('Fluid limits', f.fluidLimits()))
	print("CAS: {0}".format(f.CAS()))
	print("ASHRAE34: {0}".format(f.ASHRAE34()))
	p = (f.critical()['p'] + f.tripple()['p'])/2
	print("Saturation @ {0} bar {1}".format(p/1e5, f.saturation_p(p)))
	
	T = (f.critical()['T'] + f.tripple()['T'])/2
	print("Saturation @ {0} K {1}".format(T, f.saturation_T(T)))

def testState():
	s1 = FluidState('ParaHydrogen')
	s1.update('P', 700e5, 'T', 288)
	print("p={0}".format(s1.p()))
	print("T={0}".format(s1.T()))
	print("rho={0}".format(s1.rho()))
	print("h={0}".format(s1.h()))
	print("s={0}".format(s1.s()))
	print("cp={0}".format(s1.cp()))
	print("cv={0}".format(s1.cv()))
	print("gamma={0}".format(s1.gamma()))
	print("dpdt_v={0}".format(s1.dpdt_v()))
	print("dpdv_t={0}".format(s1.dpdv_t()))
	print("beta={0}".format(s1.beta()))
	print("mu={0}".format(s1.mu()))
	print("lambfa={0}".format(s1.cond()))
	print("Pr={0}".format(s1.Pr()))

	s2 = FluidState('ParaHydrogen')
	s2.update_Tp(s1.T(), s1.p())
	print("update_Tp rho={0}".format(s2.rho()))
	s3 = FluidState('ParaHydrogen')
	s3.update_Trho(s1.T(), s1.rho())
	print("update_Trho p={0}".format(s3.p()))
	s4 = FluidState('ParaHydrogen')
	s4.update_prho(s1.p(), s1.rho())
	print("update_prho T={0}".format(s4.T()))
	s5 = FluidState('ParaHydrogen')
	s5.update_ph(s1.p(), s1.h())
	print("update_ph ={0}".format(s5.T()))
	s6 = FluidState('ParaHydrogen')
	s6.update_ps(s1.p(), s1.s())
	print("update_ps T={0}".format(s6.T()))
	s7 = FluidState('ParaHydrogen')
	s7.update_pq(1e5, 0)
	print("update_pq T={0}".format(s7.T()))
	s8 = FluidState('ParaHydrogen')
	s8.update_Tq(25, 0)
	print("update_Tq p={0}".format(s8.p()))
	print('--------------------')
	print('Initialize state from fluid')
	h2 = Fluid('ParaHydrogen')
	s9 = FluidState(h2)
	s9.update_Tp(s1.T(), s1.p())
	print("rho={0}".format(s9.rho()))

testFluid()
print('======================')
testState()