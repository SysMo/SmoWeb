'''
Created on Mar 23, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
from pydelay import dde23
from scipy.optimize import fsolve
from smo.util import AttributeDict 
from ChemostatDDEBase import ChemostatDDEBase
from ChemostatDDEBase import plotEqulibriumValuesAtTheEnd


class ChemostatDDE2(ChemostatDDEBase):
    """
    Class for implementation the model of chemostat (2-substrates and 2-organisms) with delay differential equations (DDE) - Example 2
    """
    def __init__(self, params = None, **kwargs):   
        if params == None:
            params = AttributeDict(kwargs)
        self.params = params
        
        #Calculate the equilibrium point
        def mu1(s, m, k):
            return (m*s)/(k + s)
        
        def mu2(s, m, k, k_I):
            return (m*s)/(k + s + (s/k_I)*(s/k_I))
        
        def eq_s1(s1, *args):
            (_k1, _k2, _k3, _s1_in, _s2_in, a, m1, _m2, k_s1, _k_s2, _k_I, D, tau1, _tau2) = args
            return a*D - np.exp(-a*D*tau1) * mu1(s1, m1, k_s1)
        
        def eq_s2(s2, *args):
            (_k1, _k2, _k3, _s1_in, _s2_in, a, _m1, m2, _k_s1, k_s2, k_I, D, _tau1, tau2) = args
            return a*D - np.exp(-a*D*tau2) * mu2(s2, m2, k_s2, k_I)
        
        eqs_args = (
            params.k1, params.k2, params.k3, 
            params.s1_in, params.s2_in, params.a, 
            params.m1, params.m2, 
            params.k_s1, params.k_s2, params.k_I, 
            params.D, params.tau1, params.tau2)
        
        s1_eqpnt = fsolve(eq_s1, 1.0, args = eqs_args)[0]
        x1_eqpnt = np.exp(-params.a*params.D*params.tau1) * (params.s1_in - s1_eqpnt)/(params.a*params.k1)
        if x1_eqpnt < 0:
            s1_eqpnt = params.s1_in
            x1_eqpnt = 0.0
        
        s2_eqpnt_sol, _info, ier, _msg  = fsolve(eq_s2, 1.0, args = eqs_args, full_output = True)
        if ier != 1 or s2_eqpnt_sol[0] < 0:
            x2_eqpnt = 0.0
            s2_eqpnt = params.s2_in + params.k2*mu1(s1_eqpnt, params.m1, params.k_s1) * x1_eqpnt / params.D
        else:
            s2_eqpnt = s2_eqpnt_sol[0]
            x2_eqpnt = ((params.s2_in - s2_eqpnt)*params.D + params.k2*mu1(s1_eqpnt, params.m1, params.k_s1)*x1_eqpnt) \
                / (params.k3 * mu2(s2_eqpnt, params.m2, params.k_s2, params.k_I))
            
        self.equilibriumPoint = [s1_eqpnt, x1_eqpnt, s2_eqpnt, x2_eqpnt]
        if plotEqulibriumValuesAtTheEnd:
            print "equilibrium point (s1, x1, s2, x2) = ", self.equilibriumPoint   
        
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
            'x1': 'exp(-a*D*tau1)*mu1(s1(t-tau1), m1, k_s1)*x1(t-tau1) - a*D*x1',
            's2': 'D*(s2_in - s2) + k2*mu1(s1, m1, k_s1)*x1 - k3*mu2(s2, m2, k_s2, k_I)*x2',
            'x2': 'exp(-a*D*tau2)*mu2(s2(t-tau2), m2, k_s2, k_I)*x2(t-tau2) - a*D*x2'
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
    
def TestChemostatDDE():
    print "=== BEGIN: TestChemostatDDE ==="
    
    # Initialize simulation parameters
    solverParams = AttributeDict({
        'tFinal' : 500., 
        'tPrint' : 0.1,
        'absTol' : 1e-16,
        'relTol' : 1e-16,
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
        D = 0.1
        tau1 = 2
        tau2 = 7
        s1_hist_vals = 2.
        x1_hist_vals = 0.1
        s2_hist_vals = 10.
        x2_hist_vals = 0.05
    modelParams = ModelParams()
    
    chemostat = ChemostatDDE2(modelParams)
    chemostat.run(solverParams)
    chemostat.plotResults()
    #chemostat.plotX1X2()
    #chemostat.plotS1S2()
    #chemostat.plotS1X1()
    #chemostat.plotS2X2()
    
    print "=== END: TestChemostatDDE ==="
    
    
if __name__ == '__main__':
    TestChemostatDDE()
    