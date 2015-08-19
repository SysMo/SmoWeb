'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.model.fields as F
import smo.dynamical_models.bioreactors.ChemostatDDE2_ESA as DM

from smo.model.model import NumericalModel

class ChemostatDDE2_ESA(NumericalModel):
    label = "DDE Chemostat (Example 2 - ESA)"
    description = F.ModelDescription("Chemostat model with delay differential equations (DDE) and extremum seeking algorithm (ESA) - Example 2", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show=False)
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    # Parameters
    k1 = F.Quantity(default = 0, minValue = 0, maxValue = 1e6, label = 'k<sub>1</sub>', 
        description = 'yield coefficient related to substrate-1 consumption from bacteria-1')
    k2 = F.Quantity(default = 0, minValue = 0, maxValue = 1e6, label = 'k<sub>2</sub>', 
        description = 'yield coefficient related to substrate-2 production from bacteria-1')
    k3 = F.Quantity(default = 0, minValue = 0, maxValue = 1e6, label = 'k<sub>3</sub>', 
        description = 'yield coefficient related to substrate-2 consumption from bacteria-2')
    k4 = F.Quantity(default = 0, minValue = 0, maxValue = 1e6, label = 'k<sub>4</sub>', 
        description = 'yield coefficient of methane (biogas) on bacteria-2 and substrate-2')
    s1_in = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label ='s<sub>1</sub><sup>in</sub>', 
        description = 'input substrate-1 concentration')
    s2_in = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label ='s<sub>2</sub><sup>in</sub>', 
        description = 'input substrate-2 concentration')
    a = F.Quantity('Fraction', default = (0, '-'), label ='&#945', 
        description = 'proportion of organisms that are affected by the dilution rate D')
    D = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (0, '1/day'), label = 'D',
        description = 'dilution rate')
    parametersFG = F.FieldGroup([s1_in, s2_in, k1, k2, k3, k4, a, D], label = 'Parameters')
                        
    # Parameters - specific growth rates
    m1 = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (0, '1/day'), label = 'm<sub>1</sub>', 
        description = 'maximum specific growth rate of bacteria-1')
    m2 = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (0, '1/day'), label = 'm<sub>2</sub>', 
        description = 'maximum specific growth rate of bacteria-2')
    k_s1 = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label = 'k<sub>s1</sub>', 
        description = 'half saturation constant of bacteria-1')
    k_s2 = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label = 'k<sub>s2</sub>', 
        description = 'half saturation constant of bacteria-2')
    k_I = F.Quantity('Dimensionless', default = (0, '-'), label = 'k<sub>I</sub>', 
        description = 'constant in unit: [ sqrt( g/L ) ]')
    parametersMuFG = F.FieldGroup([m1, m2, k_s1, k_s2, k_I], label = 'Parameters - specific growth rates')
    
    # Parameters - time delays
    tau1 = F.Quantity('Bio_Time', default = (0, 'day'), minValue = (0, 'day'), label = '&#964<sub>1</sub>',
        description = 'time delay in conversion of the substrate-1 to viable biomass for bacteria-1')
    tau2 = F.Quantity('Bio_Time', default = (0, 'day'), minValue = (0, 'day'), label = '&#964<sub>2</sub>',
        description = 'time delay in conversion of the substrate-2 to viable biomass for bacteria-2')
    parametersTauFG = F.FieldGroup([tau1, tau2], label = 'Parameters - time delay')
    
    # historical initial conditions
    s1_hist_vals = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label ='s<sub>1</sub><sup>&#91-&#964<sub>1</sub>, 0&#93</sup>', 
        description = 'historical initial condition for substrate-1 concentration')
    x1_hist_vals = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label ='x<sub>1</sub><sup>&#91-&#964<sub>1</sub>, 0&#93</sup>', 
        description = 'historical initial condition for bacteria-1 concentration')
    s2_hist_vals = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label ='s<sub>2</sub><sup>&#91-&#964<sub>2</sub>, 0&#93</sup>', 
        description = 'historical initial condition for substrate-2 concentration')
    x2_hist_vals = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), label ='x<sub>2</sub><sup>&#91-&#964<sub>2</sub>, 0&#93</sup>', 
        description = 'historical initial condition for bacteria-2 concentration')
    parametersHistFG = F.FieldGroup([s1_hist_vals, x1_hist_vals, s2_hist_vals, x2_hist_vals], label = 'Historical initial conditions')
        
    inputValuesSG = F.SuperGroup([parametersMuFG, parametersFG, parametersTauFG, parametersHistFG], label = "Input values")

    #1.2 Fields - Settings
    ESA_enable = F.Boolean(default=False, label = 'enable', 
        description = 'find the the maximum methane flow rate (i.e. run extremum seeking algorithm)')
    ESA_DMin = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (0.0, '1/day'), label = 'D<sub>min</sub>',
        description = 'minimum dilution rate', show = 'self.ESA_enable')
    ESA_DMax = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (0.0, '1/day'), label = 'D<sub>max</sub>',
        description = 'maximum dilution rate', show = 'self.ESA_enable')
    ESA_eps = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (1e-9, '1/day'), maxValue = (1.0, '1/day'), 
        label = '&#949*', description = 'D max tolerance', show = 'self.ESA_enable')
    ESA_h = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (1e-8, '1/day'), maxValue = (1.0, '1/day'), 
        label = 'h*', description = 'seeking step of D max', show = 'self.ESA_enable')
    ESA_eps_z = F.Quantity('Bio_MassConcentration', default = (0, 'g/L'), minValue = (1e-9, 'g/L'), maxValue = (1.0, 'g/L'),
        label ='&#949<sub>z</sub>*', description = 'equilibrium point tolerance', show = 'self.ESA_enable')
    ESA_FG = F.FieldGroup([ESA_enable, ESA_DMin, ESA_DMax, ESA_eps, ESA_h, ESA_eps_z], label = 'Extremum Seeking Algorithm (ESA)')
    
    DsQs_DMin = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (0, '1/day'), label = 'D<sub>min</sub>',
        description = 'minimum dilution rate')
    DsQs_DMax = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (0, '1/day'), label = 'D<sub>max</sub>',
        description = 'maximum dilution rate')
    DsQs_Step = F.Quantity('Bio_TimeRate', default = (0, '1/day'), minValue = (1e-4, '1/day'), maxValue = (1.0, '1/day'), label = 'D<sub>step</sub>',
        description = 'step of dilution rate')
    DsQs_FG = F.FieldGroup([DsQs_DMin, DsQs_DMax, DsQs_Step], label = 'Chart (Ds, Qs)')
    
    tFinal = F.Quantity('Bio_Time', default = (100, 'day'), minValue = (0, 'day'), maxValue=(5000, 'day'), label = 'simulation time')
    tPrint = F.Quantity('Bio_Time', default = (0.1, 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval*')
    mainSimStep = F.Quantity('Bio_Time', default = (10., 'day'), minValue = (0.25, 'day'), maxValue = (1e3, 'day'), label = 'main simulation step*')
    absTol = F.Quantity('Bio_Time', default = (1e-12, 'day'), minValue = (1e-16, 'day'), maxValue = (1e-5, 'day'), label = 'absolute tolerance*')
    relTol = F.Quantity('Bio_Time', default = (1e-12, 'day'), minValue = (1e-16, 'day'), maxValue = (1e-3, 'day'), label = 'relative tolerance*')
    solverFG = F.FieldGroup([tFinal, tPrint, mainSimStep, absTol, relTol], label = 'Solver')
    
    settingsSG = F.SuperGroup([solverFG, DsQs_FG, ESA_FG], label = 'Settings')
    
    #1.4 Model view
    inputView = F.ModelView(ioType = "input", superGroups = [inputValuesSG, settingsSG], autoFetch = True)
    
    #2. ############ Results ###############
    # 2.1. Results
    dataSeries = (
        ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
        ('s1', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('x1', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('s2', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('x2', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('D', F.Quantity('Bio_TimeRate', default=(1, '1/day'))),
        ('Q', F.Quantity('Bio_MassConcentrationFlowRate', default=(1, 'g/L/day'))),
    )
    
    plot = F.PlotView(
        dataSeries,
        label='Plot', 
        options = {'ylabel' : None, 'title': 'Chemostat (DDE)'},
    )
    table = F.TableView(
        dataSeries,
        label='Table', 
        options = {'title': 'Title', 'formats': ['0.0000', '0.0000', '0.0000', '0.0000', '0.0000',  '0.0000',  '0.0000']}
    )

    chartS1S2 = F.MPLPlot(label = 'Chart (s<sub>1</sub>, s<sub>2</sub>)')
    chartX1X2 = F.MPLPlot(label = 'Chart (x<sub>1</sub>, x<sub>2</sub>)')
    chartS1X1 = F.MPLPlot(label = 'Chart (s<sub>1</sub>, x<sub>1</sub>)')
    chartS2X2 = F.MPLPlot(label = 'Chart (s<sub>2</sub>, x<sub>2</sub>)')
    chartS2X2 = F.MPLPlot(label = 'Chart (s<sub>2</sub>, x<sub>2</sub>)')
    chartDQ = F.MPLPlot(label = 'Chart (D, Q)')
    chartDsQs = F.MPLPlot(label = 'Chart (Ds, Qs)')

    resultsVG = F.ViewGroup([plot, table, chartS1S2, chartX1X2,  chartS1X1, chartS2X2, chartDQ, chartDsQs], label = 'Results')
    resultsSG = F.SuperGroup([resultsVG], label = "Results")
    
    # 2.2 Equilibrium point
    s1_eqpnt = F.Quantity('Bio_MassConcentration', default = (0., 'g/L'), 
        label ='s<sub>1</sub><sup>*</sup>', description = 'substrate-1 concentration at the equilibrium point')
    x1_eqpnt = F.Quantity('Bio_MassConcentration', default = (0., 'g/L'), 
        label ='x<sub>1</sub><sup>*</sup>', description = 'bacteria-1 concentration at the equilibrium point')
    s2_eqpnt = F.Quantity('Bio_MassConcentration', default = (0., 'g/L'), 
        label ='s<sub>2</sub><sup>*</sup>', description = 'substrate-2 concentration at the equilibrium point')
    x2_eqpnt = F.Quantity('Bio_MassConcentration', default = (0., 'g/L'), 
        label ='x<sub>2</sub><sup>*</sup>', description = 'bacteria-1 concentration at the equilibrium point')
    
    equilibriumPointFG = F.FieldGroup([s1_eqpnt, x1_eqpnt, s2_eqpnt, x2_eqpnt], label = 'Equilibrium point') 
    equilibriumPointSG = F.SuperGroup([equilibriumPointFG], label = 'Equilibrium point')
    
    # 2.3 ESA Results
    resESA_QMaxIsFound = F.Boolean(label = 'Q<sub>max</sub> is found')
    resESA_DMax = F.Quantity('Bio_TimeRate', default = (0, '1/day'),
        label = 'D<sub>max</sub>' , description = 'maximum dilution rate')
    resESA_QMax = F.Quantity('Bio_MassConcentrationFlowRate', default = (0, 'g/L/day'),
        label = 'Q<sub>max</sub>' , description = 'maximum methane (biogas) flow rate')
    resESA_FG = F.FieldGroup([resESA_QMaxIsFound, resESA_DMax, resESA_QMax], label = 'Results (ESA)')
    resESA_SG = F.SuperGroup([resESA_FG], label = 'Results (ESA)')
    
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsSG, resESA_SG, equilibriumPointSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    def __init__(self):
        self.k1 = (10.53, '-')
        self.k2 = (28.6, '-')
        self.k3 = (1074, '-')
        self.k4 = (100, '-')
        self.s1_in = (7.5, 'g/L')
        self.s2_in = (75, 'g/L')
        self.a = (0.5, '-')
        self.m1 = (1.2, '1/day')
        self.m2 = (0.74, '1/day')
        self.k_s1 = (7.1, 'g/L')
        self.k_s2 = (9.28, 'g/L')
        self.k_I = (16, '-')
        self.D = (0.25, '1/day')
        self.tau1 = (2, 'day')
        self.tau2 = (7, 'day')
        self.s1_hist_vals = (2, 'g/L')
        self.x1_hist_vals = (0.1, 'g/L')
        self.s2_hist_vals = (10, 'g/L')
        self.x2_hist_vals = (0.05, 'g/L')
        
        self.DsQs_DMin = (0.0, '1/day')
        self.DsQs_DMax = (1.0, '1/day')
        self.DsQs_Step = (0.01, '1/day')
        
        self.tFinal = (2000, 'day') 
        self.tPrint = (1.0, 'day') 
        self.mainSimStep = (10., 'day')
        self.absTol = (1e-12, 'day')
        self.relTol = (1e-12, 'day')
    
        self.ESA_enable = True
        self.ESA_DMin = (0.01, '1/day')
        self.ESA_DMax = (0.33, '1/day')
        self.ESA_eps = (0.01, '1/day')
        self.ESA_h = (0.025, '1/day')
        self.ESA_eps_z = (0.01, 'g/L')
        
    def compute(self):
        chemostatDDE = DM.ChemostatDDE2_ESA(self)
        if self.ESA_enable:
            chemostatDDE.runESA(self)
        else:
            chemostatDDE.run(self)

        resESA = chemostatDDE.getResultsESA()
        self.resESA_QMaxIsFound = resESA['QMaxIsFound']
        self.resESA_DMax = (resESA['DMax'], '1/day')
        self.resESA_QMax = (resESA['QMax'], 'kg/m**3/day')
        
        res = chemostatDDE.getResults()
        results = np.array([res['t'], res['s1'], res['x1'], res['s2'], res['x2'], res['D'], res['Q']]).transpose()
        self.plot = results
        self.table = results
        
        chemostatDDE.plotS1S2(self.chartS1S2)
        chemostatDDE.plotX1X2(self.chartX1X2)
        chemostatDDE.plotS1X1(self.chartS1X1)
        chemostatDDE.plotS2X2(self.chartS2X2)
        chemostatDDE.plotDQ(self.chartDQ)
        chemostatDDE.plotDsQs(self.chartDsQs)
        
        self.s1_eqpnt = (chemostatDDE.equilibriumPoint[0], 'kg/m**3')
        self.x1_eqpnt = (chemostatDDE.equilibriumPoint[1], 'kg/m**3')
        self.s2_eqpnt = (chemostatDDE.equilibriumPoint[2], 'kg/m**3')
        self.x2_eqpnt = (chemostatDDE.equilibriumPoint[3], 'kg/m**3') 
