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
csvFileName = os.path.join(tmpFolderPath, 'BioReactors_BiochemicalReactions_SimulationResults.csv')
dataStorageFilePath =  os.path.join(tmpFolderPath, 'BioReactors_SimulationResults.h5')
dataStorageDatasetPath = '/BiochemicalReactions'

""" Settings """
forwardReactionDiractions = list(['=', '<=>', '<->', '=>', '->'])
backwardReactionDiractions = list(['=', '<=>', '<->', '<=', '<-'])
validReactionDiractions = list(set(forwardReactionDiractions + backwardReactionDiractions))

class BiochemicalReactions(Simulation):
    """
    Class for implementation the model of biochemical reactions @see http://en.wikipedia.org/wiki/Rate_equation#Stoichiometric_reaction_networks
    """
    def __init__(self, params = None, **kwargs):
        """
        #params.reactions = [reactionEquation, rateConstants]
        #params.species = [speciesVariable, initialValue]
        """
        super(BiochemicalReactions, self).__init__(**kwargs)
        if params == None:
            params = AttributeDict(kwargs)
            
        # Initialize update progress function
        self.updateProgress = params.updateProgress
        
        # Get the species variables Xs = [X1, X2, ..., Xn] and their initial values
        self.Xs = np.empty(len(params.species), dtype=(np.str_, 256))
        self.X0s = np.zeros(len(params.species))
        for i, itSpecies in enumerate(params.species):
            self.Xs[i] = itSpecies[0]
            self.X0s[i] = itSpecies[1]
        
        # Get the reactions = [[left Xs, right Xs, k, ss, rs, f], ...], where: 
        # left Xs - the species variables of reactants (i.e. the species variables of the left parts of the reactions)
        # rigth Xs - the species variables of products (i.e. the species variables of the right parts of the reactions)
        # k - the rate constant of the reaction
        # ss - the stoichiometric coefficients of reactants  (e.g. [0,1,1,0,...,1])
        # rs - the stoichiometric coefficients of products (e.g. [1,0,...,0])
        # f - the fluxs (e.g. k*X2*X3*...*Xn)
        self.reactions = self.readReactions(params.reactions, self.Xs)
        #for reaction in self.reactions: print reaction
        
        # Create a vector with state variable names
        stateVarNames = list(self.Xs) 

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
        
    def readReactions(self, reactions, Xs):
        resReactions = []
        for reaction in reactions:
            txtReaction = reaction[0]
            txtReaction_orig = txtReaction
            txtReaction = txtReaction.replace(" ", "")           
            
            # Get and check the direction of the reaction
            dirReaction =  re.findall("[-=<>]+", txtReaction)
            if len(dirReaction) == 0:
                raise ValueError("\nInvalid reaction '{0}'.\nThe direction of the reaction is missing" 
                    ", use one of {1}".format(txtReaction_orig, validReactionDiractions))
            if len(dirReaction) > 1:
                raise ValueError("\nInvalid reaction '{0}'.\nToo many directions of the reaction.".format(txtReaction_orig))
            
            dirReaction = dirReaction[0]
            if not (dirReaction in validReactionDiractions):
                raise ValueError("\nInvalid reaction '{0}'.\nThe direction of the reaction '{1}' is wrong" 
                    ", use one of {2}".format(txtReaction_orig, dirReaction, validReactionDiractions))
            
            # Get and check the rate constants of the reaction
            txtRateConstants = reaction[1]
            kForward, kBackward = self.readReactionRateConstants(txtReaction_orig, txtRateConstants)
            
            if kForward == 0.0 and dirReaction in forwardReactionDiractions:
                raise ValueError("\nInvalid reaction '{0}'.\nThe direction of the reaction is '{1}', " 
                    "but the forward rate constant is {2}".format(txtReaction_orig, dirReaction, kForward))
            
            if kBackward == 0.0 and dirReaction in backwardReactionDiractions:
                raise ValueError("\nInvalid reaction '{0}'.\nThe direction of the reaction is '{1}', " 
                    "but the backward rate constant is {2}".format(txtReaction_orig, dirReaction, kBackward))
            
            # Get and check the reaction parts
            partsReaction = re.split("[-=<>]+", txtReaction)
            if len(partsReaction) <> 2:
                raise ValueError("\nInvalid reaction '{0}'.".format(txtReaction_orig))
            
            # Get and check the Xs of the leftPart of the reaction
            leftPartEq = partsReaction[0]
            leftXs = leftPartEq.split('+')
            for X in leftXs:
                if not X in Xs:
                    raise ValueError("\nInvalid reaction '{0}'.\nInvalid species variable "
                        "'{1}', use one of {2}".format(txtReaction_orig, X, Xs))
            
            rightPartEq = partsReaction[1]
            rightXs = rightPartEq.split('+')
            for X in rightXs:
                if not X in Xs:
                    raise ValueError("\nInvalid reaction '{0}'.\nInvalid species variable "
                        "'{1}', use one of {2}".format(txtReaction_orig, X, Xs))
            
            # Add to the reactions
            if dirReaction in forwardReactionDiractions:
                f = ""
                ss = np.zeros(len(Xs))
                for X in leftXs:
                    i = np.where(Xs == X)
                    ss[i] = 1
                    f += "[{0}]".format(X)
                f = "{0}".format(kForward) + f
                
                rs = np.zeros(len(Xs))
                for X in rightXs:
                    i = np.where(Xs == X)
                    rs[i] = 1             
                resReactions.append([leftXs, rightXs, kForward, ss, rs, f])
                
            if dirReaction in backwardReactionDiractions:
                f = ""
                ss = np.zeros(len(Xs))
                for X in rightXs:
                    i = np.where(Xs == X)
                    ss[i] = 1
                    f += "[{0}]".format(X)
                f = "{0}".format(kBackward) + f
                
                rs = np.zeros(len(Xs))
                for X in leftXs:
                    i = np.where(Xs == X)
                    rs[i] = 1          
                resReactions.append([rightXs, leftXs, kBackward, ss, rs, f])
                
        return resReactions
    
    def readReactionRateConstants(self, txtReaction, txtRateConstants):
        partsRate = re.split("[,;]+", txtRateConstants)
        
        if len(partsRate) == 0:
            raise ValueError("The rate constants of the reaction '{0}' are not set.\n"
                "Enter one or two rate constants with a delimiter , or ;"
                .format(txtReaction))
            
        if len(partsRate) > 2:
            raise ValueError("\Invalid rate constants '{0}' of the reaction '{1}'.\n"
                "Enter one or two rate constants with a delimiter , or ;"
                .format(txtRateConstants, txtReaction))
        
        try:
            kForward = float(partsRate[0])
        except ValueError:
            raise ValueError("\Invalid rate constants '{0}' of the reaction '{1}', \n"
                "the forward rate constant '{2}' is not valid real number."
                .format(txtRateConstants, txtReaction, partsRate[0]))
        
        kBackward = 0.0
        if len(partsRate) == 2:
            try:
                kBackward = float(partsRate[1])
            except ValueError:
                raise ValueError("\Invalid rate constants '{0}' of the reaction '{1}', \n"
                    "the backward rate constant '{2}' is not valid real number."
                    .format(txtRateConstants, txtReaction, partsRate[1]))
        
        return (kForward, kBackward)
    
    def rhs(self, t, y, sw):
        yDot = np.zeros(len(y))           
        try:
            # Compute fluxes
            fs = np.ones(len(self.reactions))
            for j, eq in enumerate(self.reactions):
                (_leftXs, _rightXs, k, ss, _rs, _f) = self.splitReaction(eq)
                fs[j] = k
                for i in range(len(y)):
                    fs[j] *= np.power(y[i], ss[i])
            
            # Compute state derivatives
            for i in range(len(y)):
                for j, eq in enumerate(self.reactions):
                    (_leftXs, _rightXs, _k, ss, rs, _f) = self.splitReaction(eq)
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
        super(BiochemicalReactions, self).handle_result(solver, t, y)
        self.updateProgress(t, self.tFinal)
        
        self.resultStorage.record[:] = (t,) + tuple(y)
        self.resultStorage.saveTimeStep()
        
    def plotHDFResults(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        
        # Get results
        self.resultStorage.openStorage()
        data = self.resultStorage.loadResult()
        
        # Plot results
        xData = data['t']
        colors = self.getColors()
        for i, X in enumerate(self.Xs):
            ax.plot(xData, data[X], '%s'%colors[i%len(colors)], label = X)
            
        self.resultStorage.closeStorage()
    
        ax.set_xlim([0, xData[-1]])
        
        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.875))
        
        # Set lables and titles
        ax.set_xlabel('Time')
        ax.set_ylabel('Concentration')
        
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
            odeTxt = r"$[{%s}]' = "%X
            for eq in self.reactions:
                (_leftXs, _rightXs, _k, ss, rs, f) = self.splitReaction(eq)
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
            for eq in self.reactions:
                (_leftXs, _rightXs, _k, ss, rs, f) = self.splitReaction(eq)
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
    
    def splitReaction(self, eq):
        return (eq[0], eq[1], eq[2], eq[3], eq[4], eq[5])
    
def TestBiochemicalReactions():
    print "=== BEGIN: TestBiochemicalReactions ==="
    
    # Settings
    simulate = True #True - run simulation; False - plot an old results
    
    # Initialize simulation parameters
    solverParams = AttributeDict({
        'tFinal' : 20., 
        'tPrint' : 0.1,
    })
    
    # Initialize model parameters
    dt = np.dtype([('reactionEquation', np.str_, 256), ('rateConstants', np.str_, 256)])
    reactions = np.array([
        ("E + S = ES", "10.1, 1.1"),  
        ("ES -> E + P", "2.1"),
    ], dtype = dt)
    
    dt_vars = np.dtype([('speciesVariable', np.str_, 256), ('initialValue', np.float64, (1))])
    species = np.array([
        ('E', 0.1),
        ('S', 0.2),
        ('ES', 0.0),
        ('P', 0.0),
    ], dtype = dt_vars)
        
    modelParams = AttributeDict({
        'reactions' : reactions,
        'species' : species,
    })
    
    # Create the model
    model = BiochemicalReactions(modelParams)
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
    
    print "=== END: TestBiochemicalReactions ==="
    
    
if __name__ == '__main__':
    TestBiochemicalReactions()
    