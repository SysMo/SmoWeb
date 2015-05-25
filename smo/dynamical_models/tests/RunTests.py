def main(plot = False):
	from ThermalMassSystem import Tank
	from smo.dynamical_models.core.TransientSimulation import TransientSimulation
	cir = Tank()
	sim = TransientSimulation(cir)
	sim.initializeModel()
	print("Initialized")
	sim.run(tFinal = 10000., tPrint = 10.)
	t = sim.result[0]
	T = sim.result[1]
	if (plot):
		import pylab as plt
		i = 0
		for state in sim.compiler.realStates:
			plt.plot(t, T[:, i], label = state.qName)
			i += 1
		plt.legend()
		plt.show()
	
def stat():
	import pstats, cProfile
	cProfile.runctx('main()', globals(), locals(), "RunProfile.prof")
	s = pstats.Stats("RunProfile.prof")
	s.strip_dirs().sort_stats("time").print_stats(20)
	
#stat()
main(plot = True)