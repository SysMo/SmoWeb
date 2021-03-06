import numpy as np
try:
    import pylab as plt
except Exception: 
    pass
from smo.math.util import Interpolator1D
from smo.media.CoolProp.CoolProp import FluidState

class Orifice(object):
    def __init__(self, diameter, cq):
        self.diameter = diameter
        self.cq = cq
    
    def computeMassFlowRate(self):
        gamma = 1.33
        pUp = 300e5
        pDown = np.linspace(100e5, 299.9e5, 1000)
        ratio = pDown/pUp
        delta = 1 - ratio
        dp = pUp - pDown
        R_g = 1
        crit_ratio = np.power(2/(gamma + 1), gamma / (gamma - 1))
        crit_delta = 1 - crit_ratio
        crit_dp = pUp * crit_delta
        print ('crit. ratio = {0}'.format(crit_ratio))
        cm = np.sqrt(2 * gamma / (R_g * (gamma - 1))) * np.sqrt(np.power(ratio, 2 / gamma) - np.power(ratio, (gamma + 1) / gamma))
        cm_crit = np.sqrt(2 * gamma / (R_g * (gamma + 1))) * np.power(2 / (gamma + 1), 1 / (gamma - 1)) * (1 + 0 * cm)
        cm_approx = np.sqrt(1 - np.power(1 - delta/crit_delta, 2)) * cm_crit
        plt.plot(ratio, cm, 'r')
        plt.plot(ratio, cm_crit, 'm')
        plt.plot(ratio, cm_approx, 'g')
        plt.plot([crit_ratio, crit_ratio], [0, np.max(cm) * 1.1], 'b')
        plt.show()
    
    @staticmethod
    def test():
        orifice = Orifice(3e-3, 1.0)
        orifice.computeMassFlowRate()

class Elbow(object):
    #r_d_90 = np.array([1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20])
    #C_d_90 = np.array([20, 14, 12, 12, 14, 17, 24, 30, 34, 38, 42, 50])
    #interp90 = scipy.interpolate.interp1d(r_d_90, C_d_90)
    A1 = Interpolator1D(
            [0, 20, 30, 45, 60, 75, 90, 110, 130, 150, 180],
            [0, 0.31, 0.45, 0.60, 0.78, 0.90, 1.0, 1.13, 1.20, 1.28, 1.40]
    )
    B1 = Interpolator1D(
            [0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.25, 1.5, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50],
            [1.18, 0.77, 0.51, 0.37, 0.28, 0.21, 0.19, 0.17, 0.15, 0.11, 0.09, 0.07, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03]
    )
    @staticmethod
    def kDelta(relRoughness):
        if (relRoughness < 1e-3):
            result = 1 + 1e3 * relRoughness
        else:
            result = 2
        return result
    
    @staticmethod
    def kRe(Re):
        result = 1.3 - 0.29 * np.log(1e-5 * Re)
        if (result < 1.0):
            result = 1.0;
        return result

    def __init__(self, internalDiameter, bendRadius, bendAngleDeg, surfaceRoughness = 0.025):
        self.internalDiameter = internalDiameter
        self.bendRadius = bendRadius
        self.bendAngleDeg = bendAngleDeg
        self.surfaceRoughness = surfaceRoughness
        self.crossSectionalArea = np.pi / 4 * self.internalDiameter**2
        self.length = self.bendAngleDeg / 180.0 * np.pi * self.bendRadius
        
        self.a1 = Elbow.A1(self.bendAngleDeg)
        self.b1 = Elbow.B1(self.bendRadius / self.internalDiameter)
        self.kd = Elbow.kDelta(self.surfaceRoughness / self.internalDiameter)
        
        print ("R_0/d", self.bendRadius / self.internalDiameter)        
        
    def setUpstreamState(self, pressure, temperature):
        fluidState = FluidState('ParaHydrogen')
        fluidState.update_Tp(temperature, pressure)
        return fluidState

    def computePressureDrop(self, upstreamState, mDot):
        self.flowVelocity = mDot / (upstreamState.rho * self.crossSectionalArea )
        self.Re = upstreamState.rho * self.flowVelocity * self.internalDiameter / upstreamState.mu
        print ('Re=', self.Re)
        
        self.cFriction = ChurchilCorrelation(self.Re, self.internalDiameter, self.surfaceRoughness) \
            * self.length / self.internalDiameter
        self.cLocal = self.a1 * self.b1 * self.kd * Elbow.kRe(self.Re)
        self.dragCoefficient =  self.cFriction + self.cLocal
        self.pressureDrop = self.dragCoefficient * upstreamState.rho * self.flowVelocity * self.flowVelocity / 2
    
        print ('cLocal=', self.cLocal)
        print ('cFriction=', self.cFriction)
        print ('dp[bar]=', self.pressureDrop/1e5)
    
    @staticmethod    
    def test():
        #a = Elbow(internalDiameter = 5.08e-2, bendRadius = 81.28e-2, bendAngleDeg = 30, surfaceRoughness = 0.00005)
        b = Elbow(internalDiameter = 3e-3, bendRadius = 16.0e-3, bendAngleDeg = 90, surfaceRoughness = 25e-6)
        upState = b.setUpstreamState(3e7, 288)
        b.computePressureDrop(upState, 100./3600)

        
def ChurchilCorrelation(Re, d, epsilon):
        theta1 = np.power(2.457 * np.log(np.power(7.0 / Re, 0.9) + 0.27 * epsilon / d), 16)
        theta2 = np.power(37530.0 / Re, 16)
        zeta = 8 * np.power(np.power((8.0 / Re), 12) + 1 / np.power((theta1 + theta2), 1.5) , 1./12)
        return zeta
    
def testChurchilCorrelation():
    Re = np.logspace(2, 6, 1000, base = 10.0)
    d = 5e-3
    epsilon = 25e-7
    zeta = 0 * Re
    for i in range(len(Re)):
        zeta[i] = ChurchilCorrelation(Re[i], d, epsilon)
    plt.loglog(Re, zeta)
    plt.show()