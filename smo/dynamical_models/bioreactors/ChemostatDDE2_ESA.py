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
from ChemostatDDEBase import ChemostatDDEBase
from ChemostatDDEBase import plotEqulibriumValuesAtTheEnd

class ChemostatDDE2_ESA(ChemostatDDEBase):
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
        
        # Initialize tauMax
        self.tauMax = np.max([self.params.tau1, self.params.tau2]) + 1 #:TRICKY: give the solver more historical data
        
        # Compute equilibrium point
        self.equilibriumPoint = self.computeEquilibriumPoint()
        if plotEqulibriumValuesAtTheEnd:
            print "equilibrium point (s1, x1, s2, x2) = ", self.equilibriumPoint
            
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
        histdic = {
            't':tau2_t_hist_vals, 
            's1':s1_hist_vals, 
            'x1':x1_hist_vals, 
            's2':s2_hist_vals, 
            'x2':x2_hist_vals}
        self.dde.hist_from_arrays(histdic)
            
    def initResults(self):
        printTimeRange = np.arange(0, self.solverParams.tFinal + self.solverParams.tPrint, self.solverParams.tPrint)
        self.tRes = printTimeRange
        self.s1Res = np.zeros(len(printTimeRange))
        self.x1Res = np.zeros(len(printTimeRange))
        self.s2Res = np.zeros(len(printTimeRange))
        self.x2Res = np.zeros(len(printTimeRange))
        self.DRes = np.zeros(len(printTimeRange))
        self.QRes = np.zeros(len(printTimeRange))
        
        # ESA Results
        self.ResESA_QMaxIsFound = False
        self.ResESA_QMax = 0.0
        self.ResESA_DMax = 0.0
        
    def getResults(self):
        return {
            't': self.tRes,
            's1': self.s1Res,
            'x1': self.x1Res,
            's2': self.s2Res,
            'x2': self.x2Res,
            'D': self.DRes,
            'Q': self.QRes,
        }
        
    def writeResultsSecSim(self, mainSimStepIndex):
        sizeResSecSim = len(np.arange(0, self.solverParams.mainSimStep + self.solverParams.tPrint, self.solverParams.tPrint)) - 1
        
        # Fetch the secondary simulation results from t=0 to t=tFinal with a step-size of dt=tPrint:
        tFinalSecSim = self.solverParams.mainSimStep
        resSecSim = self.dde.sample(0, tFinalSecSim + self.solverParams.tPrint, self.solverParams.tPrint)
        s1ResSecSim = resSecSim['s1']
        x1ResSecSim = resSecSim['x1']
        s2ResSecSim = resSecSim['s2']
        x2ResSecSim = resSecSim['x2']
        
        # Set the current point
        self.currPnt = np.array([s1ResSecSim[-1], x1ResSecSim[-1], s2ResSecSim[-1], x2ResSecSim[-1]])
        
        # Write the secondary results to the main results
        self.s1Res[sizeResSecSim * mainSimStepIndex : sizeResSecSim * (mainSimStepIndex + 1) + 1] = s1ResSecSim
        self.x1Res[sizeResSecSim * mainSimStepIndex : sizeResSecSim * (mainSimStepIndex + 1) + 1] = x1ResSecSim
        self.s2Res[sizeResSecSim * mainSimStepIndex : sizeResSecSim * (mainSimStepIndex + 1) + 1] = s2ResSecSim
        self.x2Res[sizeResSecSim * mainSimStepIndex : sizeResSecSim * (mainSimStepIndex + 1) + 1] = x2ResSecSim
        
        # Compute Qs
        QResSecSim = np.ones(sizeResSecSim + 1)
        for i in range(len(QResSecSim)):
            QResSecSim[i] = self.computeQ(s2ResSecSim[i], x2ResSecSim[i])
            
        
        # Write Ds and Qs
        self.DRes[sizeResSecSim * mainSimStepIndex : sizeResSecSim * (mainSimStepIndex + 1) + 1] = np.ones(sizeResSecSim + 1) * self.params.D
        self.QRes[sizeResSecSim * mainSimStepIndex : sizeResSecSim * (mainSimStepIndex + 1) + 1] = QResSecSim

    def runSecSim(self, tMainSim):
        params = self.params
        
        # Define the parameters
        eqns_params = {'k1':params.k1, 
            'k2':params.k2, 
            'k3':params.k3, 
            's1_in':params.s1_in, 
            's2_in':params.s2_in, 
            'a':params.a, 
            'm1':params.m1, 
            'm2':params.m2, 
            'k_s1':params.k_s1, 
            'k_s2':params.k_s2, 
            'k_I':params.k_I, 
            'D':params.D, 
            'tau1':params.tau1, 
            'tau2':params.tau2}
        
        # Initialize the solver
        self.dde = dde23(eqns=self.eqns, params=eqns_params, supportcode=self.support_c_code)
        
        # Initialize history of the state variables
        self.initHist(tMainSim)
        
        # Set the simulation parameters
        tFinalSecSim = self.solverParams.mainSimStep
        self.dde.set_sim_params(tfinal=tFinalSecSim, AbsTol=self.solverParams.absTol, RelTol=self.solverParams.relTol, dtmax=None)
        
        # Run the secondary simulation
        self.dde.run()

    def run(self, params = None, **kwargs):
        if params == None:
            params = AttributeDict(kwargs)
        self.solverParams = params
        
        # Initialize results
        self.initResults()
        
        # Run the main simulation
        mainSimStepIndex = -1
        mainSimTimeRange = np.arange(0, self.solverParams.tFinal, self.solverParams.mainSimStep)   
        for tMainSim in mainSimTimeRange:
            mainSimStepIndex += 1
            
            # Run the current secondary simulation 
            self.runSecSim(tMainSim)
            
            # Write secondary simulation results
            self.writeResultsSecSim(mainSimStepIndex)
    
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
            
            equilibriumPoint = np.array([s1_eqpnt, x1_eqpnt, s2_eqpnt, x2_eqpnt])
            
        #print "equilibrium point (s1, x1, s2, x2) = ", equilibriumPoint
        return equilibriumPoint 
    
    def computeQ(self, s2, x2):
        params = self.params
        return params.k4 * self.mu2(s2, params.m2, params.k_s2, params.k_I) * x2
    
    def computeDsQs(self):
        params = self.params
        
        # Remember D value
        D_old = params.D
        
        # Compute Qs
        D_arr = np.arange(params.DsQs_DMin, params.DsQs_DMax + params.DsQs_Step, params.DsQs_Step)
        Q_arr = np.zeros(len(D_arr))
        
        i = 0
        for D in D_arr:
            params.D = D
            
            eqPnt = self.computeEquilibriumPoint()
            [_s1_eqPnt, _x1_eqPnt, s2_eqPnt, x2_eqPnt] = eqPnt
            
            Q = self.computeQ(s2_eqPnt, x2_eqPnt)
            Q_arr[i] = Q
            i += 1
            #print "D = ", D, ", Q = ", Q, ", eqPnt = ", eqPnt
            if x2_eqPnt == 0 and D != 0.:
                break
        
        # Remove zeros elements
        D_arr = np.delete(D_arr, np.s_[i:])     
        Q_arr = np.delete(Q_arr, np.s_[i:])
        
        # Restore D
        params.D = D_old
        
        return (D_arr, Q_arr)
    
    def getResultsESA(self):
        return {
            'QMaxIsFound': self.ResESA_QMaxIsFound,
            'DMax': self.ResESA_DMax,
            'QMax': self.ResESA_QMax
        }
    
    """ Extremum Seeking Algorithm (ESA) """ 
    def runESA(self, solverParams = None, **kwargs):
        if solverParams == None:
            solverParams = AttributeDict(kwargs)
        self.solverParams = solverParams
        
        # Define helpful function
        def printStep(tMainSim, nextStep, D):
            print "\nAt time ", tMainSim, " do ", nextStep, " with D = ", D
            return
                
        # Initialize results
        self.initResults()
        
        # Initialize ESA variables
        QMaxIsFound = False
        
        eps = self.params.ESA_eps
        eps_z = self.params.ESA_eps_z
        h = self.params.ESA_h
        sigma = 1.0
        
        # Stage I
        D0 = None 
        Q0 = None
        
        D1 = None
        Q1 = None
        
        D2 = None
        Q2 = None
        
        D_minus = None
        D_plus = None
        
        # Stage II
        lmbd = (np.sqrt(5) - 1) / 2.
        
        dlt1 = None
        dlt2 = None
        dlt3 = None
        
        D0_minus = None
        D0_plus = None
        
        D1_minus = None
        D1_plus = None
        
        D_p0 = None
        Q_p0 = None
        
        D_q0 = None
        Q_q0 = None
        
        D_p1 = None
        Q_p1 = None
        
        D_q1 = None
        Q_q1 = None
         
        # Do Step I.0 of ESA
        self.params.D = (self.params.ESA_DMax + self.params.ESA_DMin) / 2.
        nextStep = 'Step I.0'
        
        # Run the main simulation
        D_prevStep = None        
        mainSimStepIndex = -1
        mainSimTimeRange = np.arange(0, self.solverParams.tFinal, self.solverParams.mainSimStep)   
        for tMainSim in mainSimTimeRange:
            mainSimStepIndex += 1
            
            # Run the secondary simulation 
            self.runSecSim(tMainSim)
            
            # Write secondary simulation results and compute Qs
            self.writeResultsSecSim(mainSimStepIndex)
            
            # Check for stabilization of the system
            if (QMaxIsFound):
                continue
            
            # Compute equilibrium and current point
            if (D_prevStep is None) or (D_prevStep != self.params.D):            
                D_prevStep = self.params.D
                eqPnt = self.computeEquilibriumPoint()
                #[_s1_eqPnt, _x1_eqPnt, s2_eqPnt, x2_eqPnt] = eqPnt
                #Q_eqPnt = self.computeQ(s2_eqPnt, x2_eqPnt)
                
            currPnt = self.currPnt
            [_s1_currPnt, _x1_currPnt, s2_currPnt, x2_currPnt] = currPnt
            Q_currPnt = self.computeQ(s2_currPnt, x2_currPnt)
            
            # Check for the equilibrium point
            if (self.distance(eqPnt, currPnt) > eps_z): #:TODO:(?) compare distance between previous point and currPnt (not between eqPnt and currPnt) 
                # The equilibrium point is not reached
                continue
            
            # Do a step of ESA (i.e. the equilibrium point is reached)
            doStep = True
           
            if nextStep == 'Step I.0' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D0 = self.params.D 
                Q0 = Q_currPnt
                
                # Go to
                nextStep = 'Step I.1'
                sigma = 1
                self.params.D = D0 + sigma*h
                
            if nextStep == 'Step I.1' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D1 = self.params.D 
                Q1 = Q_currPnt
                
                if Q1 > Q0:
                    # Go to
                    nextStep = 'Step I.3'
                    h = 2*h
                    self.params.D = D1 + sigma*h
                else:
                    # Go to
                    nextStep = 'Step I.2'
                    sigma = -1.0
                    self.params.D = D0 - sigma*h
                    
            if nextStep == 'Step I.2' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D1 = self.params.D 
                Q1 = Q_currPnt
                
                if Q1 > Q0:
                    # Go to
                    nextStep = 'Step I.3'
                    h = 2*h
                    self.params.D = D1 + sigma*h
                else:
                    h = h/2.
                    if h <= eps/2.:
                        # Go to
                        nextStep = 'Step III'
                        self.params.D = D0
                    else:
                        # Go to
                        nextStep = 'Step I.1'
                        sigma = 1
                        self.params.D = D0 + sigma*h                 
                
            if nextStep == 'Step I.3' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D2 = self.params.D 
                Q2 = Q_currPnt
                
                if Q2 <= Q1:
                    D_minus = D0
                    D_plus = D2
                    
                    # Go to
                    nextStep = 'Step II'
                    doStep = True
                else:
                    D0 = D1
                    Q0 = Q1
                    
                    D1 = D2
                    Q1 = Q2
                    
                    # Go to
                    nextStep = 'Step I.3'
                    h = 2*h
                    self.params.D = D1 + sigma*h
                    
            if nextStep == 'Step II' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D0_minus = D_minus
                D0_plus = D_plus
                print "Step II [D-, D+] = [", D0_minus, ", ", D0_plus, "]"
                
                dlt1 = D0_plus - D0_minus
                
                # Go to
                nextStep = 'Step II.0'
                doStep = True
                
            if nextStep == 'Step II.0' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                dlt2 = (1 - lmbd)*dlt1
                
                D_p0 = D0_minus + dlt2
                D_q0 = D0_plus - dlt2
                
                # Go to
                nextStep = 'Step II.1.p0'
                self.params.D = D_p0
                
            if nextStep == 'Step II.1.p0' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D_p0 = self.params.D
                Q_p0 = Q_currPnt
                
                # Go to
                nextStep = 'Step II.1.q0'
                self.params.D = D_q0
                
            if nextStep == 'Step II.1.q0' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D_q0 = self.params.D
                Q_q0 = Q_currPnt
                
                # Go to
                nextStep = 'Step II.2'
                doStep = True
                
            if nextStep == 'Step II.2' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                dlt3 = D_q0 - D_p0
                     
                if Q_p0 > Q_q0:
                    D1_minus = D0_minus
                    D1_plus = D_q0
                    D_p1 = D1_minus + dlt3
                    D_q1 = D_p0
                    Q_q1 = Q_p0 #:TODO:(?) missing in pdf
                    
                if Q_p0 <= Q_q0:
                    D1_minus = D_p0
                    D1_plus = D0_plus
                    D_p1 = D_q0
                    Q_p1 = Q_q0 #:TODO:(?) missing in pdf
                    D_q1 = D1_plus - dlt3
                    
                dlt1 = D1_plus - D1_minus
                    
                # Go to
                nextStep = 'Step II.3'
                doStep = True
            
            if nextStep == 'Step II.3' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                print "Step II.3 [D1-, D1+] = [", D1_minus, ", ", D1_plus, "]"
                
                if dlt1 <= eps:
                    # Go to
                    nextStep = 'Step III'
                    self.params.D = (D1_minus + D1_plus) / 2.
                else: # if dlt1 > eps:
                    if D_p1 >= D_q1:
                        D0_minus = D1_minus
                        D0_plus = D1_plus
                        
                        # Go to
                        nextStep = 'Step II.0'
                        doStep = True
                    else: # if D_p1 < D_q1:
                        if Q_p0 > Q_q0:
                            # Go to
                            nextStep = 'Step II.3.p1'
                            self.params.D = D_p1
                        else: # if Q_p0 >= Q_q0:
                            # Go to
                            nextStep = 'Step II.3.q1'
                            self.params.D = D_q1
                            
            if nextStep == 'Step II.3.p1' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D_p1 = self.params.D
                Q_p1 = Q_currPnt
                
                # Go to
                nextStep = 'Step II.3.1'
                doStep = True
                
            if nextStep == 'Step II.3.q1' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D_q1 = self.params.D
                Q_q1 = Q_currPnt
                
                # Go to
                nextStep = 'Step II.3.1'
                doStep = True
            
            if nextStep == 'Step II.3.1' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                D_p0 = D_p1
                D_q0 = D_q1
                
                D0_minus = D1_minus
                D0_plus = D1_plus
                
                Q_p0 = Q_p1
                Q_q0 = Q_q1
                
                # Go to
                nextStep = 'Step II.2'
                doStep = True
                
            if nextStep == 'Step III' and doStep:
                printStep(tMainSim, nextStep, self.params.D)
                doStep = False
                
                QMaxIsFound = True
                
                # Set the ESA result
                self.ResESA_QMaxIsFound = QMaxIsFound
                self.ResESA_QMax = Q_currPnt
                self.ResESA_DMax = self.params.D 
            
            #:TRICKY: limit the current seeking D value
            if self.params.D < self.params.ESA_DMin:
                self.params.D = self.params.ESA_DMin
                
            if self.params.D > self.params.ESA_DMax:
                self.params.D = self.params.ESA_DMax
            
    def distance(self, pnt1, pnt2):
        return np.max(np.abs(pnt1 - pnt2))
    
    def plotDsQs(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            
        (Ds, Qs) = self.computeDsQs()
        
        ax.plot(Ds, Qs, 'mo-', label = 'Q')
        ax.set_xlabel('D - dilution rate')
        ax.set_ylabel('Q - methane (biogas) flow rate')
        ax.legend()
        plt.show() 
        
    def plotDQ(self, ax = None):
        params = self.params
        
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
        # Plot the results    
        sol = self.getResults()
        t = sol['t']
        D = sol['D']
        Q = sol['Q']
        
        ax.plot(t, D, 'k--', linewidth=2.0, label = 'D')
        ax.plot(t, Q, 'm-', linewidth=2.0, label = 'Q')
    
        ax.set_ylim([0, 1.125*np.max(Q)])
        
        # Legend (v1)
        #box = ax.get_position()
        #ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        #ax.legend(loc='center left', bbox_to_anchor = (1, 0.9275))

        # Legend (v2)
        legentTitle = r'$\mathrm{\tau_{1} = %g,\;\tau_{2} = %g}$'%(params.tau1, params.tau2)
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.125), ncol=3, 
            fancybox=True, shadow=True, title=legentTitle, fontsize=18)
        plt.setp(legend.get_title(),fontsize=18)
        
        # Set labels
        ax.set_xlabel('D')
        ax.set_ylabel('Q')
        
        # Show
        plt.show()
            
def TestChemostatDDE():
    print "=== BEGIN: TestChemostatDDE ==="
    
    # Initialize simulation parameters
    solverParams = AttributeDict({
        'tFinal' : 5000.0, 
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
        k4 = 100.
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
        
        DsQs_DMin = 0.0
        DsQs_DMax = 1.0
        DsQs_Step = 0.01
        
        ESA_DMin = 0.22
        ESA_DMax = 0.33
        
        ESA_eps = 0.001
        ESA_h = 0.025
        ESA_eps_z = 0.01
        
    modelParams = ModelParams()
    chemostat = ChemostatDDE2_ESA(modelParams)
    
    runESA = 0
    if runESA: #run extremum seeking algorithm
        chemostat.runESA(solverParams)
        resESA = chemostat.getResultsESA()
        if resESA['QMaxIsFound']:
            print "QMax is found: (DMax, QMax) = (", resESA['DMax'], ",", resESA['QMax'], ")."
        else:
            print "QMax is not found."
        chemostat.plotAllResults()
        chemostat.plotDsQs()
    else: #run simulation
        #chemostat.run(solverParams)
        #chemostat.plotAllResults()
        #chemostat.plotResults()
        #chemostat.plotX1X2()
        #chemostat.plotS1S2()
        #chemostat.plotS1X1()
        #chemostat.plotS2X2()
        chemostat.plotDsQs()    
    
 
    print "=== END: TestChemostatDDE ==="
    
if __name__ == '__main__':
    TestChemostatDDE()