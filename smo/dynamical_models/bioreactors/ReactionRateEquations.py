'''
Created on Aprl 22, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import re
from smo.util import AttributeDict 

""" Settings """
forwardReactionDiractions = list(['=', '<=>', '<->', '=>', '->'])
backwardReactionDiractions = list(['=', '<=>', '<->', '<=', '<-'])
validReactionDiractions = list(set(forwardReactionDiractions + backwardReactionDiractions))

class ReactionRateEquations():
    """
    Class for implementation the model of reaction rate equations @see http://en.wikipedia.org/wiki/Rate_equation#Stoichiometric_reaction_networks
    """
    def __init__(self, params = None, **kwargs):   
        if params == None:
            params = AttributeDict(kwargs)
        
        self.equations = self.readEquations(params.equations, params.variables[:,0]) #[left Xs, right Xs, k]
        #for eq in self.equations: print eq
        
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
                resEquations.append([leftXs, rightXs, kForward])
                
            if dirEq in backwardReactionDiractions:            
                resEquations.append([rightXs, leftXs, kBackward])
                
        return resEquations
        
    def run(self):
        print ":TODO: Run - ReactionRateEquations"
                

def TestReactionRateEquations():
    print "=== BEGIN: TestReactionRateEquations ==="
    # Initialize model parameters
    dt = np.dtype([('equations', np.str_, 256), ('kForward', np.float64, (1)), ('kBackward', np.float64, (1))])
    equations = np.array([
        ("E + S = ES", 1.1, 2.2),
        ("E + S <=> ES", 1.1, 2.2),
        ("E + S <-> ES", 1.1, 2.2),  
        ("ES -> E + P", 1.1, 0.0),
        ("ES => E + P", 1.1, 0.0),
        ("ES <- E + P", 0.0, 2.2),
        ("ES <= E + P", 0.0, 2.2),
    ], dtype = dt)
    
    variables = np.array([
        ['E', 0.1],
        ['S', 0.1],
        ['ES', 0.1],
        ['P', 0.1],
    ])
    
    modelParams = AttributeDict({
        'equations' : equations,
        'variables' : variables,
    })
    
    # Run simulation
    model = ReactionRateEquations(modelParams)
    model.run()
    
    print "=== END: TestReactionRateEquations ==="
    
    
if __name__ == '__main__':
    TestReactionRateEquations()
    