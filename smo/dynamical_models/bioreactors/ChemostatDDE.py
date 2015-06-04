'''
Created on Mar 23, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import pylab as plt
import numpy as np
from pydelay import dde23
from smo.util import AttributeDict 
from scipy.optimize import fsolve

""" Settings """
plotEqulibriumValuesAtTheEnd = True


class ChemostatDDE():
    """
    Class for implementation the model of chemostat (2-substrates and 2-organisms) with delay differential equations (DDE)
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
    
    def run(self, params = None, **kwargs):
        if params == None:
            params = AttributeDict(kwargs)
        self.solverParams = params
                
        # Set the simulation parameters
        self.dde.set_sim_params(
            tfinal = self.solverParams.tFinal, 
            AbsTol = params.absTol, 
            RelTol = params.relTol,
            dtmax=None)
        
        # Run the simulator
        self.dde.run()
        
    def getResults(self):
        # Fetch the results from t=0 to t=tFinal with a step-size of dt=tPrint:
        return self.dde.sample(0, self.solverParams.tFinal + self.solverParams.tPrint, self.solverParams.tPrint)
        
    def plotResults(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            
        sol = self.getResults()
        t = sol['t']
        s1 = sol['s1']
        x1 = sol['x1']
        s2 = sol['s2']
        x2 = sol['x2']
        
        # Plot the results
        ax.plot(t, s1, 'r-', label = 's$_{1}$')
        ax.plot(t, x1, 'b-', label = 'x$_{1}$')
        ax.plot(t, s2, 'g-', label = 's$_{2}$')
        ax.plot(t, x2, 'm-', label = 'x$_{2}$')
        ax.set_xlabel('Time')
        ax.set_ylabel('Concentrations')
        ax.legend()
        plt.show()
        
    def plotX1X2(self, ax = None):
        params = self.params
        
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
        # Plot the results    
        sol = self.getResults()
        t = sol['t']
        x1 = sol['x1']
        x2 = sol['x2']
        
        ax.plot(t, x1, 'b-', linewidth=2.0, label = 'x$_{1}$')
        ax.plot(t, x2, 'r--', linewidth=2.0, label = 'x$_{2}$')
        
        ax.set_ylim([0, 1.25*np.max([np.max(x1), np.max(x2)])])
        
        # Legend (v1)
        #box = ax.get_position()
        #ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        #ax.legend(loc='center left', bbox_to_anchor = (1, 0.9275))

        # Legend (v2)
        legentTitle = r'$\mathrm{\bar{u} = %g,\;\tau_{1} = %g,\;\tau_{2} = %g}$'%(params.D, params.tau1, params.tau2)
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.125), ncol=3, 
            fancybox=True, shadow=True, title=legentTitle, fontsize=18)
        plt.setp(legend.get_title(),fontsize=18)
        
        if plotEqulibriumValuesAtTheEnd:
            x1 = self.equilibriumPoint[1]
            x2 = self.equilibriumPoint[3]
            ax.annotate("%.4f"%x1,xy=(t[-1], x1), xytext=(5,-3), textcoords='offset points')
            ax.annotate("%.4f"%x2,xy=(t[-1], x2), xytext=(5,-3), textcoords='offset points')
        else: 
            ax.annotate("%.2f"%x1[-1],xy=(t[-1], x1[-1]), xytext=(5,-2), textcoords='offset points')
            ax.annotate("%.2f"%x2[-1],xy=(t[-1], x2[-1]), xytext=(5,-2), textcoords='offset points')
        
        # Set labels
        ax.set_xlabel('Time')
        ax.set_ylabel('Biomass concentrations')
        
        # Show
        plt.show()
        
    def plotS1S2(self, ax = None):
        params = self.params
        
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
        # Plot the results    
        sol = self.getResults()
        t = sol['t']
        s1 = sol['s1']
        s2 = sol['s2']
        
        ax.plot(t, s1, 'g-', linewidth=2.0, label = 's$_{1}$')
        ax.plot(t, s2, 'm--', linewidth=2.0, label = 's$_{2}$')
    
        ax.set_ylim([0, 1.125*np.max([np.max(s1), np.max(s2)])])
        
        # Legend (v1)
        #box = ax.get_position()
        #ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        #ax.legend(loc='center left', bbox_to_anchor = (1, 0.9275))

        # Legend (v2)
        legentTitle = r'$\mathrm{\bar{u} = %g,\;\tau_{1} = %g,\;\tau_{2} = %g}$'%(params.D, params.tau1, params.tau2)
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.125), ncol=3, 
            fancybox=True, shadow=True, title=legentTitle, fontsize=18)
        plt.setp(legend.get_title(),fontsize=18)
        
        if plotEqulibriumValuesAtTheEnd:
            s1 = self.equilibriumPoint[0]
            s2 = self.equilibriumPoint[2]
            ax.annotate("%.4f"%s1,xy=(t[-1], s1), xytext=(5,-3), textcoords='offset points')
            ax.annotate("%.4f"%s2,xy=(t[-1], s2), xytext=(5,-3), textcoords='offset points')
        else: 
            ax.annotate("%.2f"%s1[-1],xy=(t[-1], s1[-1]), xytext=(5,-3), textcoords='offset points')
            ax.annotate("%.2f"%s2[-1],xy=(t[-1], s2[-1]), xytext=(5,-3), textcoords='offset points')
        
        # Set labels
        ax.set_xlabel('Time')
        ax.set_ylabel('Substrate concentrations')
        
        # Show
        plt.show()
        

def TestChemostatDDE():
    print "=== BEGIN: TestChemostatDDE ==="
    
    # Initialize simulation parameters
    solverParams = AttributeDict({
        'tFinal' : 5., 
        'tPrint' : 1.,
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
        D = 0.85
        tau1 = 2
        tau2 = 7
        s1_hist_vals = 2.
        x1_hist_vals = 0.1
        s2_hist_vals = 10.
        x2_hist_vals = 0.05
    modelParams = ModelParams()
    
    chemostat = ChemostatDDE(modelParams)
    chemostat.run(solverParams)
    #chemostat.plotResults()
    chemostat.plotX1X2()
    chemostat.plotS1S2()
    
    print "=== END: TestChemostatDDE ==="
    
    
if __name__ == '__main__':
    TestChemostatDDE()
    