'''
Created on Mar 23, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import pylab as plt
import numpy as np
#from pydelay import dde23
from smo.util import AttributeDict 
#from scipy.optimize import fsolve

""" Settings """
plotEqulibriumValuesAtTheEnd = False

class ChemostatDDEBase():
    """
    Class for implementation the model of chemostat (2-substrates and 2-organisms) with delay differential equations (DDE)
    """
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
        
    def plotAllResults(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            
        sol = self.getResults()
        t = sol['t']
        s1 = sol['s1']
        x1 = sol['x1']
        s2 = sol['s2']
        x2 = sol['x2']
        D = sol['D']
        Q = sol['Q']
        
        # Plot the results
        ax.plot(t, s1, 'r-', label = 's$_{1}$')
        ax.plot(t, x1, 'b-', label = 'x$_{1}$')
        ax.plot(t, s2, 'g-', label = 's$_{2}$')
        ax.plot(t, x2, 'm-', label = 'x$_{2}$')
        ax.plot(t, D, 'c--', label = 'D')
        ax.plot(t, Q, 'k--', label = 'Q')
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
        
    def plotS1X1(self, ax = None):
        params = self.params
        
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
        # Plot the results    
        sol = self.getResults()
        s1 = sol['s1']
        x1 = sol['x1']
        
        ax.plot(s1, x1, 'g-', linewidth=2.0, label = '_nolegend_')
        ax.plot(s1[0], x1[0], 'bo', label = 'initial point', markersize=8)
        if plotEqulibriumValuesAtTheEnd:
            ax.plot(s1[-1], x1[-1], 'rD', label = 'equilibrium point', markersize=8)
        else:
            ax.plot(s1[-1], x1[-1], 'rD', label = 'end point', markersize=8)
        
        ax.set_xlim(0)
        ax.set_ylim([0, 1.135*np.max(x1)])
        
        # Legend (v2)
        legentTitle = r'$\mathrm{\bar{u} = %g,\;\tau_{1} = %g,\;\tau_{2} = %g}$'%(params.D, params.tau1, params.tau2)
        legend = ax.legend(
            loc='upper center', bbox_to_anchor=(0.5, 1.125), ncol=3, 
            fancybox=True, shadow=True, title=legentTitle, fontsize=14,
            numpoints=1)
        plt.setp(legend.get_title(),fontsize=18)
        
        if plotEqulibriumValuesAtTheEnd:
            s1 = self.equilibriumPoint[0]
            x1 = self.equilibriumPoint[1]
            ax.annotate("(%.4f, %.4f)"%(s1, x1),xy=(s1, x1), xytext=(7,-3), textcoords='offset points')
        else: 
            ax.annotate("(%.2f, %.2f)"%(s1[-1], x1[-1]),xy=(s1[-1], x1[-1]), xytext=(7,-3), textcoords='offset points')
        
        # Set labels
        ax.set_xlabel('$s_1$', fontsize=20)
        ax.set_ylabel('$x_1$', fontsize=20)
        
        # Show
        plt.show()
        
    def plotS2X2(self, ax = None):
        params = self.params
        
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
        # Plot the results    
        sol = self.getResults()
        s2 = sol['s2']
        x2 = sol['x2']
        
        ax.plot(s2, x2, 'g-', linewidth=2.0, label = '_nolegend_')
        ax.plot(s2[0], x2[0], 'bo', label = 'initial point', markersize=8)
        if plotEqulibriumValuesAtTheEnd:
            ax.plot(s2[-1], x2[-1], 'rD', label = 'equilibrium point', markersize=8)
        else:
            ax.plot(s2[-1], x2[-1], 'rD', label = 'end point', markersize=8)
        
        ax.set_xlim(0)
        ax.set_ylim([0, 1.135*np.max(x2)])
        
        
        # Legend (v2)
        legentTitle = r'$\mathrm{\bar{u} = %g,\;\tau_{1} = %g,\;\tau_{2} = %g}$'%(params.D, params.tau1, params.tau2)
        legend = ax.legend(
            loc='upper center', bbox_to_anchor=(0.5, 1.125), ncol=3, 
            fancybox=True, shadow=True, title=legentTitle, fontsize=14,
            numpoints=1)
        plt.setp(legend.get_title(),fontsize=18)
        
        if plotEqulibriumValuesAtTheEnd:
            s2 = self.equilibriumPoint[2]
            x2 = self.equilibriumPoint[3]
            ax.annotate("(%.4f, %.4f)"%(s2, x2),xy=(s2, x2), xytext=(7,-3), textcoords='offset points')
        else: 
            ax.annotate("(%.2f, %.2f)"%(s2[-1], x2[-1]),xy=(s2[-1], x2[-1]), xytext=(7,-3), textcoords='offset points')
        
        # Set labels
        ax.set_xlabel('$s_2$', fontsize=20)
        ax.set_ylabel('$x_2$', fontsize=20)
        
        # Show
        plt.show()