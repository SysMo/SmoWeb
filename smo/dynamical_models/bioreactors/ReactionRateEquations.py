'''
Created on Aprl 22, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import pylab as plt
import numpy as np
import re

from smo.dynamical_models.core.Simulation import Simulation, ResultStorage
from smo.util import AttributeDict 

""" Global Settings """
import os
from SmoWeb.settings import MEDIA_ROOT
tmpFolderPath = os.path.join (MEDIA_ROOT, 'tmp')
csvFileName = os.path.join(tmpFolderPath, 'BioReactors_ReactionRateEquations_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'BioReactors_SimulationResults.h5')
dataStorageDatasetPath = '/ReactionRateEquations'

""" Settings """
forwardReactionDiractions = list(['=', '<=>', '<->', '=>', '->'])
backwardReactionDiractions = list(['=', '<=>', '<->', '<=', '<-'])
validReactionDiractions = list(set(forwardReactionDiractions + backwardReactionDiractions))

class ReactionRateEquations(Simulation):
    """
    Class for implementation the model of reaction rate equations @see http://en.wikipedia.org/wiki/Rate_equation#Stoichiometric_reaction_networks
    """
    def __init__(self, params = None, **kwargs):
        """
        #params.equations = [Eqs, kForward, kBackward]
        #params.variables = [Xs, X0s]
        """
        super(ReactionRateEquations, self).__init__(**kwargs)
        if params == None:
            params = AttributeDict(kwargs)
        
        # Get the variables Xs = [X1, X2, ..., Xn] 
        self.Xs = np.empty(len(params.variables), dtype=(np.str_, 256))
        self.X0s = np.zeros(len(params.variables))
        for i, var in enumerate(params.variables):
            self.Xs[i] = var[0]
            self.X0s[i] = var[1]
        
        # Get the equations = [[left Xs, right Xs, k, ss, rs, f], ...], where: 
        # left Xs - the variables of reactants (i.e. the variables of the left parts of the equations)
        # rigth Xs - the variables of products (i.e. the variables of the right parts of the equations)
        # k - the rate constant of the reaction
        # ss - the stoichiometric coefficients of reactants  (e.g. [0,1,1,0,...,1])
        # rs - the stoichiometric coefficients of products (e.g. [1,0,...,0])
        # f - the fluxs (e.g. k*X2*X3*Xn)
        self.equations = self.readEquations(params.equations, self.Xs)
        #for eq in self.equations: print eq
        
        # Create state vector and derivative vector
        stateVarNames = list(self.Xs) 
        #self.y = NamedStateVector(stateVarNames)
        #self.yRes = NamedStateVector(stateVarNames)
        #self.yDot = NamedStateVector(stateVarNames)
        

        # Initialize data storage
        self.resultStorage = ResultStorage(
            filePath = dataStorageFilePath,
            datasetPath = dataStorageDatasetPath)
        if (kwargs.get('initDataStorage', True)):
            self.resultStorage.initializeWriting(
                varList = ['t'] + stateVarNames,
                chunkSize = 1e4)
        
        # Set the initial state values
        self.y0 = self.X0s
        
        # Set the initial flags
        self.sw0 = [True]
        
    def readEquations(self, equations, Xs):
        resEquations = []
        for rowEq in equations:
            txtEq = rowEq[0]
            txtEq_orig = txtEq
            txtEq = txtEq.replace(" ", "")           
            
            # Get and check the direction of the equation
            dirEq =  re.findall("[-=<>]+", txtEq)
            if len(dirEq) == 0:
                raise ValueError("\nInvalid equation '{0}'.\nThe direction of the reaction is missing" 
                    ", use one of {1}".format(txtEq_orig, validReactionDiractions))
            if len(dirEq) > 1:
                raise ValueError("\nInvalid equation '{0}'.\nToo many directions of the reaction.".format(txtEq_orig))
            
            dirEq = dirEq[0]
            if not (dirEq in validReactionDiractions):
                raise ValueError("\nInvalid equation '{0}'.\nThe direction of the reaction '{1}' is wrong" 
                    ", use one of {2}".format(txtEq_orig, dirEq, validReactionDiractions))
                
            kForward = rowEq[1]
            if kForward == 0.0 and dirEq in forwardReactionDiractions:
                raise ValueError("\nInvalid equation '{0}'.\nThe direction of the reaction is '{1}', " 
                    "but the forward rate constant is {2}".format(txtEq_orig, dirEq, kForward))
                 
            kBackward = rowEq[2]
            if kBackward == 0.0 and dirEq in backwardReactionDiractions:
                raise ValueError("\nInvalid equation '{0}'.\nThe direction of the reaction is '{1}', " 
                    "but the backward rate constant is {2}".format(txtEq_orig, dirEq, kBackward))
            
            # Get and check the equation parts
            partsEq = re.split("[-=<>]+", txtEq)
            if len(partsEq) <> 2:
                raise ValueError("\nInvalid equation '{0}'.".format(txtEq_orig))
            
            # Get and check the Xs of the leftPart of the equation
            leftPartEq = partsEq[0]
            leftXs = leftPartEq.split('+')
            for X in leftXs:
                if not X in Xs:
                    raise ValueError("\nInvalid equation '{0}'.\nThe invalid variable"
                        "'{1}', use one of {2}".format(txtEq_orig, X, Xs))
            
            rightPartEq = partsEq[1]
            rightXs = rightPartEq.split('+')
            for X in rightXs:
                if not X in Xs:
                    raise ValueError("\nInvalid equation '{0}'.\nThe invalid variable"
                        "'{1}', use one of {2}".format(txtEq_orig, X, Xs))
            
            # Add to the equations
            if dirEq in forwardReactionDiractions:
                f = ""
                ss = np.zeros(len(Xs))
                for X in leftXs:
                    i = np.where(Xs == X)
                    ss[i] = 1
                    f += "*{0}".format(X)
                f = "{0}".format(kForward) + f
                
                rs = np.zeros(len(Xs))
                for X in rightXs:
                    i = np.where(Xs == X)
                    rs[i] = 1             
                resEquations.append([leftXs, rightXs, kForward, ss, rs, f])
                
            if dirEq in backwardReactionDiractions:
                f = ""
                ss = np.zeros(len(Xs))
                for X in rightXs:
                    i = np.where(Xs == X)
                    ss[i] = 1
                    f += "*{0}".format(X)
                f = "{0}".format(kBackward) + f
                
                rs = np.zeros(len(Xs))
                for X in leftXs:
                    i = np.where(Xs == X)
                    rs[i] = 1          
                resEquations.append([rightXs, leftXs, kBackward, ss, rs, f])
                
        return resEquations
    
    def rhs(self, t, y, sw):
        yDot = np.zeros(len(y))           
        try:
            # Compute fluxes
            fs = np.ones(len(self.equations))
            for j, eq in enumerate(self.equations):
                (_leftXs, _rightXs, k, ss, _rs, _f) = self.splitEquation(eq)
                fs[j] = k
                for i in range(len(y)):
                    fs[j] *= np.power(y[i], ss[i])
            
            # Compute state derivatives
            for i in range(len(y)):
                for j, eq in enumerate(self.equations):
                    (_leftXs, _rightXs, _k, ss, rs, _f) = self.splitEquation(eq)
                    S = rs[i] - ss[i]
                    yDot[i] += S*fs[j]
                
        except Exception, e:
            self.resultStorage.finalizeResult()
            # Log the error if it happens in the rhs() function
            print("Exception at time {}: {}".format(t, e))
            raise e
            
        return yDot
    
    def state_events(self, t, y, sw):
        eventIndicators = np.ones(len(sw))
        return eventIndicators
    
    def step_events(self, solver):
        pass
    
    def handle_event(self, solver, eventInfo):
        pass
    
    def handle_result(self, solver, t, y):
        super(ReactionRateEquations, self).handle_result(solver, t, y)
        
        self.resultStorage.record[:] = (t,) + tuple(y)
        self.resultStorage.saveTimeStep()
        
    def getResults(self):
        return self.resultStorage.data
    
    def loadResult(self, simIndex):
        self.resultStorage.loadResult(simIndex)
        
    def plotHDFResults(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
        # Get results
        data = self.resultStorage.data
        
        # Plot results
        xData = data['t']
        colors = self.getColors()
        for i, X in enumerate(self.Xs):
            ax.plot(xData, data[X], '%s'%colors[i%len(colors)], label = X)
    
        ax.set_xlim([0, xData[-1]])
        
        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.875))
        
        # Set lables and titles
        ax.set_xlabel('Time [day]')
        ax.set_ylabel('Variables [g/L]')
        
        #plt.title('Reaction rate equations')
        
        plt.show()
        
    def getColors(self):
        colors_base = ['r-', 'b-', 'g-', 'm-', 'y-', 'c-', 'k-']
        colors = []
        colors += colors_base
        colors += ['%s-'%c for c in colors_base]
        colors += ['%s.'%c for c in colors_base]
        return colors
        
    def plotODEsTxt(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        ax.set_frame_on(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        
        # Plot settings
        xCoord = 0.0
        yCoord = 0.9  
        yCoordOffset = -0.1
        fontsize = 24  
        
        # Plot ODEs
        for i, X in enumerate(self.Xs):
            odeTxt = r"${%s}\mathtt{\/}' = "%X
            for eq in self.equations:
                (_leftXs, _rightXs, _k, ss, rs, f) = self.splitEquation(eq)
                S = rs[i] - ss[i]
                if S < 0.0:
                    if odeTxt.endswith("= "):
                        odeTxt += r"-{0}".format(f)
                    else:
                        odeTxt += r" - {0}".format(f)
                if S > 0.0:
                    if odeTxt.endswith("= "):
                        odeTxt += r"{0}".format(f)
                    else:
                        odeTxt += r" + {0}".format(f)
            odeTxt += "$"
            ax.text(xCoord, yCoord, odeTxt, fontsize=fontsize)
            yCoord += yCoordOffset  

        # Show plot
        plt.show()
 
    def getODEsTxt(self):
        resTxt = ""
        for i, X in enumerate(self.Xs):
            resTxt += "{0}' = ".format(X)
            for eq in self.equations:
                (_leftXs, _rightXs, _k, ss, rs, f) = self.splitEquation(eq)
                S = rs[i] - ss[i]
                if S < 0.0:
                    if resTxt.endswith("= "):
                        resTxt += "-{0}".format(f)
                    else:
                        resTxt += " - {0}".format(f)
                if S > 0.0:
                    if resTxt.endswith("= "):
                        resTxt += "{0}".format(f)
                    else:
                        resTxt += " + {0}".format(f)
            resTxt += "\n"
        return resTxt
    
    def splitEquation(self, eq):
        return (eq[0], eq[1], eq[2], eq[3], eq[4], eq[5])
    
def TestReactionRateEquations():
    print "=== BEGIN: TestReactionRateEquations ==="
    
    # Settings
    simulate = True #True - run simulation; False - plot an old results
    
    # Initialize simulation parameters
    solverParams = AttributeDict({
        'tFinal' : 20., 
        'tPrint' : 0.1,
    })
    
    # Initialize model parameters
    dt = np.dtype([('equations', np.str_, 256), ('kForward', np.float64, (1)), ('kBackward', np.float64, (1))])
    equations = np.array([
        ("E + S = ES", 10.1, 1.1),
        #("E + S <=> ES", 1.1, 2.2),
        #("E + S <-> ES", 1.1, 2.2),  
        ("ES -> E + P", 1.1, 0.0),
        #("ES => E + P", 1.1, 0.0),
        #("ES <- E + P", 0.0, 2.2),
        #("ES <= E + P", 0.0, 2.2),
    ], dtype = dt)
    
    dt_vars = np.dtype([('variables', np.str_, 256), ('initValue', np.float64, (1))])
    variables = np.array([
        ('E', 0.1),
        ('S', 0.2),
        ('ES', 0.0),
        ('P', 0.0),
    ], dtype = dt_vars)
        
    modelParams = AttributeDict({
        'equations' : equations,
        'variables' : variables,
    })
    
    # Create the model
    model = ReactionRateEquations(modelParams)
    print model.getODEsTxt()
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    model.plotODEsTxt(ax)
    
    # Run simulation or load old results
    if (simulate == True):
        model.prepareSimulation()
        model.run(solverParams)
    else:
        model.loadResult(simIndex = 1)
    
    # Export to csv file
    #model.resultStorage.exportToCsv(fileName = csvFileName)
    
    # Plot results
    fig = plt.figure()
    ax = fig.add_subplot(111)
    model.plotHDFResults(ax)
    
    print "=== END: TestReactionRateEquations ==="
    
    
if __name__ == '__main__':
    TestReactionRateEquations()
    