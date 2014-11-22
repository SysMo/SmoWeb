from smo.smoflow3d.CoolProp.CoolProp import Fluid, FluidState

def testFluid():
	#f = Fluid('R134a')
	f = Fluid('ParaHydrogen')
	#f = Fluid('Water')
	BibTexKeys = ["EOS", "CP0", "VISCOSITY", "CONDUCTIVITY",
						 "ECS_LENNARD_JONES", "ECS_FITS", "SURFACE_TENSION"]
	for key in BibTexKeys:
		print("{0} : {1}".format(key, f.get_BibTeXKey(key)))
	
	print("{0} : {1}".format('EOS reference', f.get_EOSReference()))
	print("{0} : {1}".format('Transpor reference', f.get_TransportReference()))
		
	print("{0} : {1} [g/mol]".format('Molar mass', f.molarMass()))
	print("{0} : {1}".format('Accentric factor', f.accentricFactor()))
	print("{0} : {1}".format('Critical point', f.critical()))
	print("{0} : {1}".format('Tripple point', f.tripple()))
	print("{0} : {1}".format('Fluid limits', f.fluidLimits()))
	
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

testFluid()
print('======================')
testState()