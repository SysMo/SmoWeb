'''
Created on Apr 16, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
from smo.media.CoolProp5.CoolProp import AbstractState
from smo.media.CoolProp5._constants import PT_INPUTS, HmassP_INPUTS

class FluidState(AbstractState):
    """ 
    Class representing a CoolProp5 fluid
    """
    # Construct methods
    def __init__(self, backend, fluidName):
        super(FluidState, self).__init__(backend, fluidName)
        self.updated = False
        
    def setMassFraction(self, massFraction):
        super(FluidState, self).set_mass_fractions([massFraction])
        
    # Update methods
    def checkUpdated(self):
        if (not self.updated):
            raise RuntimeError("In order to read a property, you must first call one of the 'update' functions")

    def update_Tp(self, T, p):
        super(FluidState, self).update(PT_INPUTS, p, T)
        self.updated = True
        
    def update_ph(self, p, h):
        super(FluidState, self).update(HmassP_INPUTS, h, p)
        self.updated = True
        
    # Get methods   
    @property
    def T(self):
        """temperature""" 
        self.checkUpdated()
        return super(FluidState, self).T()
    
    @property
    def p(self):
        """pressure"""
        self.checkUpdated()
        return super(FluidState, self).p()
    
    @property
    def rho(self):
        """density"""
        self.checkUpdated()
        return super(FluidState, self).rhomass()

    @property
    def v(self):
        """specific volume"""
        self.checkUpdated()
        return 1./self.rho
    
    @property
    def h(self):
        """specific enthalpy"""
        self.checkUpdated()
        return super(FluidState, self).hmass() 
    
    @property
    def q(self):
        """vapor quality"""
        self.checkUpdated()
        raise RuntimeError("The property 'vapor quality' of CoolProp5.FluidState is not implemented!")
    
    @property
    def u(self):
        """specific internal energy"""
        self.checkUpdated()
        return super(FluidState, self).umass()
    
    @property
    def s(self):
        """specific entropy""" 
        self.checkUpdated()
        return super(FluidState, self).smass()
    
    @property
    def cp(self):
        """specific heat capacity at constant pressure"""
        self.checkUpdated()
        return super(FluidState, self).cpmass()
    
    @property
    def cv(self):
        """specific heat capacity at constant volume"""
        self.checkUpdated()
        return super(FluidState, self).cvmass()
    
    @property
    def mu(self):
        """dynamic viscosity"""
        self.checkUpdated()
        return super(FluidState, self).viscosity()
    
    @property
    def cond(self):
        """thermal conductivity"""
        self.checkUpdated()
        return super(FluidState, self).conductivity()
    
    @property
    def Pr(self):
        """Prandtl number"""
        self.checkUpdated()
        return super(FluidState, self).Prandtl()
    
class FluidStateFactory():
    @staticmethod
    def createIncompressibleSolution(solutionName, massFraction):
        fState = FluidState('INCOMP', solutionName)
        fState.setMassFraction(massFraction)
        return fState
        
def testFluidState():
    fState = FluidStateFactory.createIncompressibleSolution('MEG', 0.5)
    fState.update_Tp(300, 1e5)
    
    print "T = ", fState.T
    print "p = ", fState.p
    print "rho = ", fState.rho
    print "v = ", fState.v
    print "h = ", fState.h
    print "u = ", fState.u
    print "s = ", fState.s
    print "cp = ", fState.cp
    print "cv = ", fState.cv
    print "mu = ", fState.mu
    print "cond = ", fState.cond
    print "Pr = ", fState.Pr
    
    
def testCoolProp5():
    f1 = AbstractState('INCOMP', 'MEG')
    f1.set_mass_fractions([0.5])
    f1.update(PT_INPUTS, 1e5, 275, )
    
    print "rho [kg/m**3] = ", f1.rhomass()
    print "cp [kJ/kg-K] = ", f1.cpmass() / 1e3
    print "lambda [W/K-m] = ", f1.conductivity()
    print "nu [mm**2/s]= ", 1e-6 * f1.viscosity() / f1.rhomass()
    
if __name__ == "__main__":
    #testCoolProp5()
    testFluidState()