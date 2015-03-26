'''
Created on March 23, 2015

@author: Milen Borisov
'''
import pylab as plt
from pydelay import dde23


""" Classes """
class AnaerobicDigestionDDE():
    """
    Class for implementation the model of anaerobid digestion (2-substrates and 2-organisms) with delay differential equations (DDE)
    """
    def __init__(self, model):
        # Define the specific growth rates (in 'C' source code)
        c_code = """
        double mu1(double s, double m, double k) {
            return (m*s)/(k + s);
        }
        
        double mu2(double s, double m, double k, double k_I) {
            return (m*s)/(k + s + (s/k_I)*(s/k_I));
        }
        """
        
        # Define the equations
        eqns = {
            's1': 'D*(s1_in - s1) - k1*mu1(s1, m1, k_s1)*x1',
            'x1': 'mu1(s1(t-tau1), m1, k_s1)*x1(t-tau1) - a*D*x1',
            's2': 'D*(s2_in - s2) + k2*mu1(s1, m1, k_s1)*x1 - k3*mu2(s2, m2, k_s2, k_I)*x2',
            'x2': 'mu2(s2(t-tau2), m2, k_s2, k_I)*x2(t-tau2) - a*D*x2'
        }
        
        # Define the parameters
        params = {
            'k1'    : model.k1,
            'k2'    : model.k2,
            'k3'    : model.k3,
            's1_in' : model.s1_in,
            's2_in' : model.s2_in,
            'a'     : model.a,
            'm1'    : model.m1,
            'm2'    : model.m2,
            'k_s1'  : model.k_s1,
            'k_s2'  : model.k_s2,
            'k_I'   : model.k_I,
            'D'     : model.D,
            'tau1'  : model.tau1,
            'tau2'  : model.tau2,
        }
        
        # Initialize the solver
        self.dde = dde23(eqns=eqns, params=params, supportcode=c_code)

        # Set the initial conditions (i.e. set the history of the state variables)
        histfunc = {
            's1': lambda t: model.s1_hist_vals,
            'x1': lambda t: model.x1_hist_vals,
            's2': lambda t: model.s2_hist_vals,
            'x2': lambda t: model.x2_hist_vals
            }
        self.dde.hist_from_funcs(histfunc, 4.)
                
    
    def run(self, solver):
        # Set the simulation parameters
        self.dde.set_sim_params(tfinal=solver.tFinal, dtmax=None)
        
        # Run the simulator
        self.dde.run()
        
        
    def plotResults(self, solver):
        # Fetch the results from t=0 to t=tFinal with a step-size of dt=tPrint:
        sol = self.dde.sample(0, solver.tFinal+solver.tPrint, solver.tPrint)
        t = sol['t']
        s1 = sol['s1']
        x1 = sol['x1']
        s2 = sol['s2']
        x2 = sol['x2']
        
        # Plot the results
        plt.plot(t, s1, 'r-', label='s1(t)')
        plt.plot(t, x1, 'b-', label='x1(t)')
        plt.plot(t, s2, 'g-', label='s2(t)')
        plt.plot(t, x2, 'm-', label='x2(t)')
        plt.xlabel('$t$')
        plt.legend()
        plt.show()
        

""" Test functions """
def TestAnaerobicDigestionDDE():
    print "=== BEGIN: Test TestAnaerobicDigestionDDE ==="
    
    # Initialize simulation parameters
    class SolverParams():
        tFinal = 50.
        tPrint = 0.1
    solverParams = SolverParams()
        
    # Initialize model parameters
    class ModelParams():
        k1 = 10.53
        k2 = 28.6
        k3 = 1074.
        s1_in = 7.5
        s2_in = 75.
        a = 0.5
        m1 = 1.2
        m2 = 0.74
        k_s1 = 7.1
        k_s2 = 9.28
        k_I = 16.
        D = 0.89
        tau1 = 2.
        tau2 = 3.
        s1_hist_vals = 3.
        x1_hist_vals = 0.7
        s2_hist_vals = 12.
        x2_hist_vals = 0.1
    modelParams = ModelParams()
    
    model = AnaerobicDigestionDDE(modelParams)
    model.run(solverParams)
    model.plotResults(solverParams)
    
    print "=== END: Test TestAnaerobicDigestionDDE ==="
    
if __name__ == '__main__':
    TestAnaerobicDigestionDDE()
    