'''
Created on March 23, 2015

@author: Milen Borisov
'''
import pylab as plt
from pydelay import dde23
from smo.util import AttributeDict 

class ChemostatDDE():
    """
    Class for implementation the model of chemostat (2-substrates and 2-organisms) with delay differential equations (DDE)
    """
    def __init__(self, params = None, **kwargs):   
        if params == None:
            params = AttributeDict(kwargs)
        
        # Define the specific growth rates (in 'C' source code)
        support_c_code = """
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
        eqns_params = {
            'k1'    : params.k1,
            'k2'    : params.k2,
            'k3'    : params.k3,
            's1_in' : params.s1_in,
            's2_in' : params.s2_in,
            'a'     : params.a,
            'm1'    : params.m1,
            'm2'    : params.m2,
            'k_s1'  : params.k_s1,
            'k_s2'  : params.k_s2,
            'k_I'   : params.k_I,
            'D'     : params.D,
            'tau1'  : params.tau1,
            'tau2'  : params.tau2,
        }
        
        # Initialize the solver
        self.dde = dde23(eqns=eqns, params=eqns_params, supportcode=support_c_code)

        # Set the initial conditions (i.e. set the history of the state variables)
        histfunc = {
            's1': lambda t: params.s1_hist_vals,
            'x1': lambda t: params.x1_hist_vals,
            's2': lambda t: params.s2_hist_vals,
            'x2': lambda t: params.x2_hist_vals
            }
        self.dde.hist_from_funcs(histfunc, 10.) #:TRICKY: 10. is 'nn' - sample in the interval
                
    
    def run(self, params = None, **kwargs):
        if params == None:
            params = AttributeDict(kwargs)
        self.solverParams = params
                
        # Set the simulation parameters
        self.dde.set_sim_params(tfinal=self.solverParams.tFinal, dtmax=None)
        
        # Run the simulator
        self.dde.run()
        
    def getResults(self):
        # Fetch the results from t=0 to t=tFinal with a step-size of dt=tPrint:
        return self.dde.sample(0, self.solverParams.tFinal + self.solverParams.tPrint, self.solverParams.tPrint)
        
    def plotResults(self):
        sol = self.getResults()
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
        

def TestChemostatDDE():
    print "=== BEGIN: TestChemostatDDE ==="
    
    # Initialize simulation parameters
    solverParams = AttributeDict({
        'tFinal' : 50., 
        'tPrint' : 0.1
    })
        
    # Initialize model parameters
    class ModelParams(): #:TRICKY: here it is also possible to use AttributeDict instead of class ModelParams
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
    
    chemostat = ChemostatDDE(modelParams)
    chemostat.run(solverParams)
    chemostat.plotResults()
    
    print "=== END: TestChemostatDDE ==="
    
    
if __name__ == '__main__':
    TestChemostatDDE()
    