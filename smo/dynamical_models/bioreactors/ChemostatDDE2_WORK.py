'''
Created on Mar 23, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import pylab as plt
from pydelay import dde23
from scipy.optimize import fsolve
from smo.util import AttributeDict

PRINT_DEBUG = 0

class ChemostatDDE2():
    """
    Class for implementation the model of chemostat (2-substrates and 2-organisms) with delay differential equations (DDE) - Example 2
    """
    def __init__(self, params = None, **kwargs):   
        if params == None:
            params = AttributeDict(kwargs)
        self.params = params
        
        # Define the specific growth rates (in 'C' source code)
        self.support_c_code = """
        double mu1(double s, double m, double k) {
            return (m*s)/(k + s);
        }
        
        double mu2(double s, double m, double k, double k_I) {
            return (m*s)/(k + s + (s/k_I)*(s/k_I));
        }
        """
        
        # Define the equations
        self.eqns = {
            's1': 'D*(s1_in - s1) - k1*mu1(s1, m1, k_s1)*x1',
            'x1': 'exp(-a*D*tau1)*mu1(s1(t-tau1), m1, k_s1)*x1(t-tau1) - a*D*x1',
            's2': 'D*(s2_in - s2) + k2*mu1(s1, m1, k_s1)*x1 - k3*mu2(s2, m2, k_s2, k_I)*x2',
            'x2': 'exp(-a*D*tau2)*mu2(s2(t-tau2), m2, k_s2, k_I)*x2(t-tau2) - a*D*x2'
        }
        
        # Define the parameters
        self.eqns_params = {
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
        
        # Initialize tauMax
        self.tauMax = np.max([self.params.tau1, self.params.tau2]) + 1 #:TRICKY: give the solver more historical data
            
    def initHist(self, tMainSim):       
        if (self.params.tau1 == 0 and self.params.tau2 == 0):
            if tMainSim == 0:
                histfunc = {
                    's1': lambda t: self.params.s1_hist_vals,
                    'x1': lambda t: self.params.x1_hist_vals,
                    's2': lambda t: self.params.s2_hist_vals,
                    'x2': lambda t: self.params.x2_hist_vals
                }
            else:
                tMainSimIndex = np.searchsorted(self.tRes, tMainSim)
                histfunc = {
                    's1': lambda t: self.s1Res[tMainSimIndex],
                    'x1': lambda t: self.x1Res[tMainSimIndex],
                    's2': lambda t: self.s2Res[tMainSimIndex],
                    'x2': lambda t: self.x2Res[tMainSimIndex]
                }
            self.dde.hist_from_funcs(histfunc, 10.) #:TRICKY: 10. is 'nn' - sample in the interval
            return
        
        if PRINT_DEBUG:
            print ""
            print "tMainSim: ", tMainSim
        tau1 = self.tauMax
        if (tMainSim < tau1):
            tau1_t_hist_vals = np.linspace(0, tau1 - tMainSim, 9)
            s1_hist_vals = np.ones(len(tau1_t_hist_vals)) * self.params.s1_hist_vals
            x1_hist_vals = np.ones(len(tau1_t_hist_vals)) * self.params.x1_hist_vals
            if tMainSim > 0:
                tau1_t_hist_begin = 0
                tau1_t_hist_end = tMainSim
                tau1_t_hist_begin_index = np.searchsorted(self.tRes, tau1_t_hist_begin)
                tau1_t_hist_end_index = np.searchsorted(self.tRes, tau1_t_hist_end)
                tau1_t_hist_vals = np.delete(tau1_t_hist_vals, -1)
                tau1_t_hist_vals = np.concatenate([
                        tau1_t_hist_vals, 
                        self.tRes[tau1_t_hist_begin_index:tau1_t_hist_end_index + 1] + tau1 - tMainSim])
                s1_hist_vals = np.delete(s1_hist_vals, -1)
                s1_hist_vals = np.concatenate([
                        s1_hist_vals, 
                        self.s1Res[tau1_t_hist_begin_index:tau1_t_hist_end_index + 1]])
                x1_hist_vals = np.delete(x1_hist_vals, -1)
                x1_hist_vals = np.concatenate([
                        x1_hist_vals, 
                        self.x1Res[tau1_t_hist_begin_index:tau1_t_hist_end_index + 1]])
        else:
            tau1_t_hist_begin = tMainSim - tau1
            tau1_t_hist_begin_index = np.searchsorted(self.tRes, tau1_t_hist_begin)
            tau1_t_hist_end = tMainSim
            tau1_t_hist_end_index = np.searchsorted(self.tRes, tau1_t_hist_end)
            tau1_t_hist_vals = self.tRes[tau1_t_hist_begin_index:tau1_t_hist_end_index + 1] - self.tRes[tau1_t_hist_begin_index]
            s1_hist_vals = self.s1Res[tau1_t_hist_begin_index:tau1_t_hist_end_index + 1]
            x1_hist_vals = self.x1Res[tau1_t_hist_begin_index:tau1_t_hist_end_index + 1]
            if PRINT_DEBUG:
                print "t_hist_vals: ", tau1_t_hist_vals + self.tRes[tau1_t_hist_begin_index]
        if PRINT_DEBUG:
            print "tau1_t_hist_vals: ", tau1_t_hist_vals
            print "s1_hist_vals: ", s1_hist_vals
            print "x1_hist_vals: ", x1_hist_vals
        tau2 = self.tauMax
        if (tMainSim < tau2):
            tau2_t_hist_vals = np.linspace(0, tau2 - tMainSim, 9)
            s2_hist_vals = np.ones(len(tau2_t_hist_vals)) * self.params.s2_hist_vals
            x2_hist_vals = np.ones(len(tau2_t_hist_vals)) * self.params.x2_hist_vals
            if tMainSim > 0:
                tau2_t_hist_begin = 0
                tau2_t_hist_end = tMainSim
                tau2_t_hist_begin_index = np.searchsorted(self.tRes, tau2_t_hist_begin)
                tau2_t_hist_end_index = np.searchsorted(self.tRes, tau2_t_hist_end)
                tau2_t_hist_vals = np.delete(tau2_t_hist_vals, -1)
                tau2_t_hist_vals = np.concatenate([
                        tau2_t_hist_vals, 
                        self.tRes[tau2_t_hist_begin_index:tau2_t_hist_end_index + 1] + tau2 - tMainSim])
                s2_hist_vals = np.delete(s2_hist_vals, -1)
                s2_hist_vals = np.concatenate([
                        s2_hist_vals, 
                        self.s2Res[tau2_t_hist_begin_index:tau2_t_hist_end_index + 1]])
                x2_hist_vals = np.delete(x2_hist_vals, -1)
                x2_hist_vals = np.concatenate([
                        x2_hist_vals, 
                        self.x2Res[tau2_t_hist_begin_index:tau2_t_hist_end_index + 1]])
        else:
            tau2_t_hist_begin = tMainSim - tau2
            tau2_t_hist_begin_index = np.searchsorted(self.tRes, tau2_t_hist_begin)
            tau2_t_hist_end = tMainSim
            tau2_t_hist_end_index = np.searchsorted(self.tRes, tau2_t_hist_end)
            tau2_t_hist_vals = self.tRes[tau2_t_hist_begin_index:tau2_t_hist_end_index + 1] - self.tRes[tau2_t_hist_begin_index]
            s2_hist_vals = self.s2Res[tau2_t_hist_begin_index:tau2_t_hist_end_index + 1]
            x2_hist_vals = self.x2Res[tau2_t_hist_begin_index:tau2_t_hist_end_index + 1]
        if PRINT_DEBUG:
            print "tau2_t_hist_vals: ", tau2_t_hist_vals
            print "s2_hist_vals: ", s2_hist_vals
            print "x2_hist_vals: ", x2_hist_vals
        histdic = {
            't':tau2_t_hist_vals, 
            's1':s1_hist_vals, 
            'x1':x1_hist_vals, 
            's2':s2_hist_vals, 
            'x2':x2_hist_vals}
        self.dde.hist_from_arrays(histdic)


    def writeResults(self, mainSimStepIndex):
        tFinalSecSim = self.solverParams.mainSimStep
        # Fetch the secondary simulation results from t=0 to t=tFinal with a step-size of dt=tPrint:
        res = self.dde.sample(0, tFinalSecSim + self.solverParams.tPrint, self.solverParams.tPrint)
        s1 = res['s1']
        x1 = res['x1']
        s2 = res['s2']
        x2 = res['x2']
        
        # Write the secondary results to the main results
        self.s1Res[self.sizeResSecSim * mainSimStepIndex : self.sizeResSecSim * (mainSimStepIndex + 1) + 1] = s1
        self.x1Res[self.sizeResSecSim * mainSimStepIndex : self.sizeResSecSim * (mainSimStepIndex + 1) + 1] = x1
        self.s2Res[self.sizeResSecSim * mainSimStepIndex : self.sizeResSecSim * (mainSimStepIndex + 1) + 1] = s2
        self.x2Res[self.sizeResSecSim * mainSimStepIndex : self.sizeResSecSim * (mainSimStepIndex + 1) + 1] = x2
        if PRINT_DEBUG:
            print "---"
            print "s1Res: ", self.s1Res
            print "x1Res: ", self.x1Res
            print "s2Res: ", self.s2Res
            print "x2Res: ", self.x2Res
            print ""

    def run(self, params = None, **kwargs):
        if params == None:
            params = AttributeDict(kwargs)
        self.solverParams = params
        
        # Initialize results
        printTimeRange = np.arange(0, self.solverParams.tFinal + self.solverParams.tPrint, self.solverParams.tPrint)
        self.tRes = printTimeRange
        self.s1Res = np.zeros(len(printTimeRange))
        self.x1Res = np.zeros(len(printTimeRange))
        self.s2Res = np.zeros(len(printTimeRange))
        self.x2Res = np.zeros(len(printTimeRange))
        
        # Run the main simulation
        mainSimTimeRange = np.arange(0, self.solverParams.tFinal, self.solverParams.mainSimStep)
        self.sizeResSecSim = len(np.arange(0, self.solverParams.mainSimStep + self.solverParams.tPrint, self.solverParams.tPrint)) - 1
               
        mainSimStepIndex = -1
        for tMainSim in mainSimTimeRange:
            mainSimStepIndex += 1
             
            # Change dilution rate
            if mainSimStepIndex == 10:
                self.eqns_params['D'] = self.params.D + 0.1
            
            if mainSimStepIndex == 20:
                self.eqns_params['D'] = self.params.D + 0.2
            
            # Initialize the solver
            self.dde = dde23(eqns=self.eqns, params=self.eqns_params, supportcode=self.support_c_code)

            # Initialize history of the state variables   
            self.initHist(tMainSim)
                
            # Set the simulation parameters
            tFinalSecSim = self.solverParams.mainSimStep
            self.dde.set_sim_params(
                tfinal = tFinalSecSim, 
                AbsTol = params.absTol, 
                RelTol = params.relTol,
                dtmax = None)
        
            # Run the secondary simulation
            self.dde.run()
            
            # Write results
            self.writeResults(mainSimStepIndex)
            
    def mu1(self, s, m, k):
        return (m*s)/(k + s)
    
    def mu2(self, s, m, k, k_I):
        return (m*s)/(k + s + (s/k_I)*(s/k_I))
    
    def computeEquilibriumPoint(self):
        params = self.params
        
        # Define equations
        mu1 = self.mu1
        mu2 = self.mu2
        
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
        
        # Compute equilibrium point
        if params.D == 0:
            equilibriumPoint = [0., 0., 0., 0.]
        else:
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
            
            equilibriumPoint = [s1_eqpnt, x1_eqpnt, s2_eqpnt, x2_eqpnt]
            
        #print "equilibrium point (s1, x1, s2, x2) = ", equilibriumPoint
        return equilibriumPoint 
    
    def computeQ(self, s2, x2):
        params = self.params
        return params.k4 * self.mu2(s2, params.m2, params.k_s2, params.k_I) * x2
            
    def plotQ2D(self):
        params = self.params
        
        # Compute Qs
        step = 0.001
        D_arr = np.arange(0, 1 + step, step)
        Q_arr = np.zeros(len(D_arr))
        
        i = 0
        for D in D_arr:
            params.D = D
            
            eqPnt = self.computeEquilibriumPoint()
            [_eqPnt_s1, _eqPnt_x1, eqPnt_s2, eqPnt_x2] = eqPnt
            
            Q = self.computeQ(eqPnt_s2, eqPnt_x2)
            Q_arr[i] = Q
            i += 1
            #print "D = ", D, ", Q = ", Q, ", eqPnt = ", eqPnt
            if eqPnt_x2 == 0 and D != 0.:
                break
        
        # Remove zeros elements
        D_arr = np.delete(D_arr, np.s_[i:])     
        Q_arr = np.delete(Q_arr, np.s_[i:])     
        #print D_arr, Q_arr
        
        # Plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        ax.plot(D_arr, Q_arr, 'ro-', label = 'Q')
        ax.set_xlabel('D - dilution rate')
        ax.set_ylabel('Q - methane (biogas) flow rate')
        ax.legend()
        plt.show() 
    
    def plotResults(self, ax = None):        
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        t = self.tRes
        s1 = self.s1Res
        x1 = self.x1Res
        s2 = self.s2Res
        x2 = self.x2Res
        
        # Plot the results
        ax.plot(t, s1, 'r-', label = 's$_{1}$')
        ax.plot(t, x1, 'b-', label = 'x$_{1}$')
        ax.plot(t, s2, 'g-', label = 's$_{2}$')
        ax.plot(t, x2, 'm-', label = 'x$_{2}$')
        ax.set_xlabel('Time')
        ax.set_ylabel('Concentrations')
        ax.legend()
        plt.show()        
  
def TestChemostatDDE():
    print "=== BEGIN: TestChemostatDDE ==="
    
    # Initialize simulation parameters
    solverParams = AttributeDict({
        'tFinal' : 500.0, 
        'tPrint' : 0.1,
        'absTol' : 1e-16,
        'relTol' : 1e-16,
        'mainSimStep': 10.
    })
        
    # Initialize model parameters
    class ModelParams(): #:TRICKY: here it is also possible to use AttributeDict instead of class ModelParams
        k1 = 10.53
        k2 = 28.6
        k3 = 1074.
        k4 = 1.
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
    #chemostat.run(solverParams)
    #chemostat.plotResults()
    chemostat.plotQ2D()
     
    print "=== END: TestChemostatDDE ==="
    
    
if __name__ == '__main__':
    TestChemostatDDE()