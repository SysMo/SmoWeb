from smo.media.CoolProp.CoolProp import FluidState
from smo.model.model import NumericalModel
from smo.model.actions import ServerAction, ActionBar
from smo.model.fields import *
from smo.media.MaterialData import Fluids
from collections import OrderedDict


StateVariableOptions = OrderedDict((
    ('P', 'pressure (P)'),
    ('T', 'temperature (T)'),
    ('D', 'density (D)'),
    ('H', 'specific enthalpy (H)'),
    ('S', 'specific entropy (S)'),
    ('Q', 'vapor quality (Q)'),
))

TransitionType = OrderedDict((
    #('P', 'isobaric (const. p)'),
    ('T', 'isothermal (const. T)'),
    #('D', 'isochoric (const. v)'),
    ('H', 'isenthalpic (const. h)'),
    ('S', 'isentropic (const. s)'),
))


from smo.media.calculators.ThermodynamicProcesses import IsentropicExpansion, IsentropicCompression, \
                                                        IsothermalExpansion, IsothermalCompression, \
                                                        IsenthalpicExpansion
class CompressionExpansionModel(NumericalModel):
    label = "Compression / Expansion"
    
    # 1. ############ Inputs ###############
    # 1.1 Input values
    
    fluidName = Choices(options = Fluids, default = 'ParaHydrogen', label = 'fluid')    
    stateVariable1 = Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')
    p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable1 == 'P'")
    T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable1 == 'T'")
    rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable1 == 'D'")
    h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable1 == 'H'")
    s1 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable1 == 'S'")
    q1 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable1 == 'Q'")
    stateVariable2 = Choices(options = StateVariableOptions, default = 'T', label = 'second state variable')
    p2 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable2 == 'P'")
    T2 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable2 == 'T'")
    rho2 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable2 == 'D'")
    h2 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable2 == 'H'")
    s2 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable2 == 'S'")
    q2 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable2 == 'Q'")
    mDot = Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'mass flow')
    initialState = FieldGroup([fluidName, stateVariable1, p1, T1, rho1, h1, s1, q1, stateVariable2, p2, T2, rho2, h2, s2, q2, mDot], label = 'Initial state')

    transitionType = Choices(options = TransitionType, default = 'S', label = "process type")
#     stateVariable_final = Choices(options = OrderedDict((('T', 'temperature (T)'), ('Q', 'vapor quality (Q)'))), 
#                                     default = 'T', label = 'state variable', show="self.transitionType == 'T'")    
    p_final = Quantity('Pressure', default = (1, 'bar'), label = 'pressure')
#     T_final = Quantity('Temperature', default = (300, 'K'), label = 'temperature', 
#                         show="self.transitionType == 'T' && self.stateVariable_final == 'T'")
#     q_final = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', 
#                         show="self.transitionType == 'T' && self.stateVariable_final == 'Q'")
    eta = Quantity(default = 1, minValue = 0, maxValue = 1, label = 'efficiency')
    heatOutFraction = Quantity(default = 0.1, minValue = 0, maxValue = 1, label = 'released heat fraction')
    finalState = FieldGroup([transitionType, p_final, eta, heatOutFraction], label = 'Final state')
    
    inputs = SuperGroup([initialState, finalState])
    
    # Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    # Model View
    inputView = ModelView(ioType = "input", superGroups = [inputs], 
        actionBar = inputActionBar, autoFetch = True)

    ############# Results ###############
    # Initial state
    T_i = Quantity('Temperature', label = 'temperature')
    p_i = Quantity('Pressure', label = 'pressure')
    rho_i = Quantity('Density', label = 'density')
    h_i = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
    s_i = Quantity('SpecificEntropy', label = 'specific entropy')
    q_i = Quantity('VaporQuality', label = 'vapor quality')
    u_i = Quantity('SpecificInternalEnergy', label = 'specific internal energy')    
    initialStateResults = FieldGroup([T_i, p_i, rho_i, h_i, s_i, q_i, u_i], label = 'Initial state')

    # Final state
    T_f = Quantity('Temperature', label = 'temperature')
    p_f = Quantity('Pressure', label = 'pressure')
    rho_f = Quantity('Density', label = 'density')
    h_f = Quantity('SpecificEnthalpy', label = 'specific enthalpy')
    s_f = Quantity('SpecificEntropy', label = 'specific entropy')
    q_f = Quantity('VaporQuality', label = 'vapor quality')
    u_f = Quantity('SpecificInternalEnergy', label = 'specific internal energy')    
    finalStateResults = FieldGroup([T_f, p_f, rho_f, h_f, s_f, q_f, u_f], label = 'Final state')
    
    stateResults = SuperGroup([initialStateResults, finalStateResults], label = "States")
    # Specific enetry quantities
    wIdeal = Quantity('SpecificEnergy', label = "ideal work")
    wReal = Quantity('SpecificEnergy', label = "real work")
    deltaH = Quantity('SpecificEnthalpy', label = 'enthalpy change (fluid)') 
    qOut = Quantity('SpecificEnergy', label = "heat released")
    qFluid = Quantity('SpecificEnergy', label = "heat to fluid")
    specificEnergyResults = FieldGroup([wIdeal, wReal, deltaH, qOut, qFluid], label = "Heat/work (specific quantities)")
    # Energy flow quantities
    wDotIdeal = Quantity('Power', label = "ideal work")
    wDotReal = Quantity('Power', label = "real work")
    deltaHDot = Quantity('Power', label = 'enthalpy change (fluid)') 
    qDotOut = Quantity('HeatFlowRate', label = "heat released")
    qDotFluid = Quantity('HeatFlowRate', label = "heat to fluid")
    energyFlowResults = FieldGroup([wDotIdeal, wDotReal, deltaHDot, qDotOut, qDotFluid], label = "Heat/work flows")

    energyBalanceResults = SuperGroup([specificEnergyResults, energyFlowResults], label = "Energy balance")
    
    # Model View
    resultView = ModelView(ioType = "output", superGroups = [stateResults, energyBalanceResults])

    ############# Page structure ########
    modelBlocks = [inputView, resultView]

    ############# Methods ###############
    def getStateValue(self, sVar, prefix = "", suffix=""):
        sVarDict = {'P': 'p', 'T': 'T', 'D': 'rho', 'H': 'h', 'S': 's', 'Q': 'q'}
        return self.__dict__[prefix + sVarDict[sVar] + suffix]

    def compute(self):
        initState = FluidState(self.fluidName)
        
        # Compute initial state
        initState.update(
                self.stateVariable1, self.getStateValue(self.stateVariable1, suffix = "1"), 
                self.stateVariable2, self.getStateValue(self.stateVariable2, suffix = "2")
        )
        self.T_i = initState.T
        self.p_i = initState.p
        self.rho_i = initState.rho
        self.h_i = initState.h
        self.s_i = initState.s
        self.q_i = initState.q
        self.u_i = initState.u
        
        if self.p_final > initState.p:
            if self.transitionType == 'S':
                process = IsentropicCompression(self.fluidName, self.eta, self.heatOutFraction)
            elif self.transitionType == 'H':
                raise ValueError('For isenthalpic expansion the final pressure must be lower than the initial pressure.')
            elif self.transitionType == 'T':
                process = IsothermalCompression(self.fluidName, self.eta, self.heatOutFraction)
        else:
            if self.transitionType == 'S':
                process = IsentropicExpansion(self.fluidName, self.eta, self.heatOutFraction)
            elif self.transitionType == 'H':
                process = IsenthalpicExpansion(self.fluidName, self.eta, self.heatOutFraction)
            elif self.transitionType == 'T':
                process = IsothermalExpansion(self.fluidName, self.eta, self.heatOutFraction)
        
        process.initState = initState
        process.compute(constantStateVariable = self.transitionType, 
                                finalStateVariable = 'P', 
                                finalStateVariableValue = self.p_final, 
                                mDot = self.mDot)
        
        self.T_f = process.T_f
        self.p_f = process.p_f
        self.rho_f = process.rho_f
        self.h_f = process.h_f
        self.s_f = process.s_f
        self.q_f = process.q_f
        self.u_f = process.u_f
        
        self.wIdeal = process.wIdeal
        self.wReal = process.wReal
        self.qOut = process.qOut
        self.qFluid = process.qFluid

        self.wDotIdeal = process.wDotIdeal
        self.wDotReal = process.wDotReal
        self.deltaHDot = process.deltaHDot
        self.qDotOut = process.qDotOut
        self.qDotFluid = process.qDotFluid

from smo.media.calculators.ThermodynamicProcesses import HeatingCooling
class HeatingCoolingModel(NumericalModel):
    label = "Heating / Cooling"
    
    ############ Inputs ###############
    fluidName = Choices(options = Fluids, default = 'ParaHydrogen', label = 'fluid')    
    stateVariable1 = Choices(options = StateVariableOptions, default = 'P', label = 'first state variable')
    p1 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable1 == 'P'")
    T1 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable1 == 'T'")
    rho1 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable1 == 'D'")
    h1 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable1 == 'H'")
    s1 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable1 == 'S'")
    q1 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable1 == 'Q'")
    stateVariable2 = Choices(options = StateVariableOptions, default = 'T', label = 'second state variable')
    p2 = Quantity('Pressure', default = (1, 'bar'), label = 'pressure', show="self.stateVariable2 == 'P'")
    T2 = Quantity('Temperature', default = (300, 'K'), label = 'temperature', show="self.stateVariable2 == 'T'")
    rho2 = Quantity('Density', default = (1, 'kg/m**3'), label = 'density', show="self.stateVariable2 == 'D'")
    h2 = Quantity('SpecificEnthalpy', default = (1000, 'kJ/kg'), label = 'specific enthalpy', show="self.stateVariable2 == 'H'")
    s2 = Quantity('SpecificEntropy', default = (100, 'kJ/kg-K'), label = 'specific entropy', show="self.stateVariable2 == 'S'")
    q2 = Quantity('VaporQuality', default = (1, '-'), minValue = 0, maxValue = 1, label = 'vapour quality', show="self.stateVariable2 == 'Q'")
    mDot = Quantity('MassFlowRate', default = (1, 'kg/h'), label = 'mass flow')
    initialState = FieldGroup([fluidName, stateVariable1, p1, T1, rho1, h1, s1, q1, stateVariable2, p2, T2, rho2, h2, s2, q2, mDot], label = 'Initial state')

    T_final = Quantity('Temperature', default = (300, 'K'), label = 'temperature')
    q_final = Quantity('VaporQuality', label = 'vapor quality')
    finalState = FieldGroup([T_final, q_final], label = 'Final state')
    inputs = SuperGroup([initialState, finalState])
    
    # Actions
    computeAction = ServerAction("compute", label = "Compute", outputView = 'resultView')
    inputActionBar = ActionBar([computeAction], save = True)
    
    # Model View
    inputView = ModelView(ioType = "input", superGroups = [inputs], 
        actionBar = inputActionBar, autoFetch = True)
    
    ############# Results ###############
    
    # Model View
    resultView = ModelView(ioType = "output", superGroups = [])

    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    ############# Methods ###############
    def compute(self):
        pass