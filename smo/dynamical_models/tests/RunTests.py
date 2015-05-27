def plotResults(sim):
	t = sim.result[0]
	T = sim.result[1]
	import pylab as plt
	i = 0
	for state in sim.compiler.realStates:
		plt.plot(t, T[:, i], label = state.qName)
		i += 1
	plt.legend()
	plt.show()

def runThermalMass(plot = False):
	from ThermalMassSystem import Tank
	from smo.dynamical_models.core.TransientSimulation import TransientSimulation
	cir = Tank()
	sim = TransientSimulation(cir)
	sim.initializeModel()
	print("Initialized")
	sim.run(tFinal = 10000., tPrint = 10.)
	if (plot):
		plotResults(sim)

		
def runMechanicalMass(plot = False):
	from MechanicalSystem import MechSystem
	from smo.dynamical_models.core.TransientSimulation import TransientSimulation
	cir = MechSystem()
	sim = TransientSimulation(cir)
	sim.initializeModel()
	sim.run(tFinal = 10., tPrint = 0.1)
	if (plot):
		plotResults(sim)
	

def main(plot):
	#runThermalMass(plot)
	runMechanicalMass(plot)
	
def stat():
	import pstats, cProfile
	cProfile.runctx('main()', globals(), locals(), "RunProfile.prof")
	s = pstats.Stats("RunProfile.prof")
	s.strip_dirs().sort_stats("time").print_stats(20)
	
#stat()
main(plot = True)