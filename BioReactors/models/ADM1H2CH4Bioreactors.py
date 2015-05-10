'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import numpy as np
import smo.model.fields as F
import smo.model.actions as A 
import smo.dynamical_models.bioreactors.ADM1H2Bioreactor as DM

from smo.model.model import NumericalModel
#from smo.web.modules import RestModule

class SolverSettings(NumericalModel):
    tFinal = F.Quantity('Bio_Time', default = (0., 'day'), minValue = (0, 'day'), maxValue=(1000, 'day'), label = 'simulation time')
    tPrint = F.Quantity('Bio_Time', default = (0., 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval')
    
    FG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    SG = F.SuperGroup([FG], label = 'Settings')
    
    modelBlocks = []
    
class H2Bioreactor(NumericalModel):
    # Stoichiometric parameter values
    f_ch_xc = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>ch,xc</sub>', description = 'yield of carbohydrates on composites')
    f_pr_xc = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>pr,xc</sub>', description = 'yield of proteins on composites')
    f_li_xc = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>li,xc</sub>', description = 'yield of lipids on composites')
    
    f_fa_li = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>fa,li</sub>', description = 'yield of LCFA on lipids')
    
    f_ac_su = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>ac,su</sub>', description = 'yield of acetate on sugars')
    f_h2_su = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>h2,su</sub>', description = 'yield of hydrogen on sugars')
    
    f_ac_aa = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>ac,aa</sub>', description = 'yield of acetate on amino acids')
    f_h2_aa = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>h2,aa</sub>', description = 'yield of hydrogen on amino acids')
    
    Y_su = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>su</sub>', description = 'yield of sugar degraders on sugars')
    Y_aa = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>aa</sub>', description = 'yield of amino acids degraders on amino acids')
    Y_fa = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>fa</sub>', description = 'yield of LCFA degraders on LCFA')
    
    stoichiometricParametersFG = F.FieldGroup([
            f_ch_xc, f_pr_xc, f_li_xc, f_fa_li, f_ac_su, f_h2_su,
            f_ac_aa, f_h2_aa, Y_su, Y_aa, Y_fa
        ],
        label = 'Stoichiometric parameters (R-H2)'
    )
    
    # Biochemical parameter values
    k_dis = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>dis</sub>', description = 'rate coefficient for disintegration of composites')
    
    k_hyd_ch = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>hyd,ch</sub>', description = 'rate coefficient for hydrolysis of carbohydrates')
    k_hyd_pr = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>hyd,pr</sub>', description = 'rate coefficient for hydrolysis of proteins')
    k_hyd_li = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>hyd,li</sub>', description = 'rate coefficient for hydrolysis of lipids') 
    
    k_m_su = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,su</sub>', description = 'specific Monod maximum uptake rate of sugar degraders')
    K_S_su = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'K<sub>S,su</sub>', description = 'Monod half saturation constant of sugar degraders')
    
    k_m_aa = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,aa</sub>', description = 'specific Monod maximum uptake rate of amino acids degraders')
    K_S_aa = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'K<sub>S,aa</sub>', description = 'Monod half saturation constant of amino acids degraders')
    
    k_m_fa = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,fa</sub>', description = 'specific Monod maximum uptake rate of LCFA degraders')
    K_S_fa = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'K<sub>S,fa</sub>', description = 'Monod half saturation constant of LCFA degraders')
    
    biochemicalParametersFG = F.FieldGroup([
            k_dis, k_hyd_ch, k_hyd_pr, k_hyd_li,
            k_m_su, K_S_su, k_m_aa, K_S_aa, k_m_fa, K_S_fa, 
        ],
        label = 'Biochemical parameters (R-H2)'
    )
    
    # Physiochemical parameters (Temperatures)
    T_base = F.Quantity('Temperature', default = (0.0, 'degC'),
        label = 'T<sub>base</sub>', description = 'base (ambient) temperature')
    T_op = F.Quantity('Temperature', default = (0.0, 'degC'),
        label = 'T<sub>op</sub>', description = 'operating temperature')
    
    temperatureParametersFG = F.FieldGroup([
            T_base, T_op,
        ],
        label = 'Temperatures (R-H2)'
    )
    
    # Physiochemical parameters
    kLa_h2 = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>L</sub>a<sub> h2</sub>', description = 'gas-liquid transfer coefficient of hydrogen')

    physiochemicalParametersFG = F.FieldGroup([
           kLa_h2,
        ],
        label = 'Physiochemical parameters (R-H2)'
    )

    # Physical parameters
    V_liq = F.Quantity('Volume', default = (0.0, 'L'),
        label = 'V<sub>liq</sub>', description = 'volume of the liquid part of the reactor')
    V_gas = F.Quantity('Volume', default = (0.0, 'L'),
        label = 'V<sub>gas</sub>', description = 'volume of the gas headspace of the reactor')

    physicalParametersFG = F.FieldGroup([
            V_liq, V_gas,
        ],
        label = 'Physical parameters (R-H2)'
    )
    
    # Volumetri flow rates
    q_liq_vals = F.RecordArray(
        (
            ('time', F.Quantity('Bio_Time', default = (10.0, 'day'), minValue = (0, 'day'), label = 'Duration')),
            ('q', F.Quantity('Bio_VolumetricFlowRate', default = (0.17, 'L/day'), minValue = (0, 'L/day'), label = 'Flow rate')),
        ), 
        label = 'q<sub> liq</sub>', 
        description = 'liquid flow rate (dilution/wash-out)',
        toggle = True,
    ) 
    
    q_gas = F.Quantity('Bio_VolumetricFlowRate', default = (0.0, 'L/day'), minValue = (0, 'L/day'), 
        label = 'q<sub> gas</sub>', description = 'gas flow rate (wash-out)')

    volumetricFlowRatesFG = F.FieldGroup([
            q_liq_vals, q_gas
        ],
        label = 'Volumetric flow rates (R-H2)' #'Controller
    )
    
    # Input concentrations of components
    S_su_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>su</sub><sup> (in)</sup>', description = 'input concentration of sugars')

    S_aa_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>aa</sub><sup> (in)</sup>', description = 'input concentration of amino acids')

    S_fa_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>fa</sub><sup> (in)</sup>', description = 'input concentration of fatty acids (LCFA)')

    S_ac_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>ac</sub><sup> (in)</sup>', description = 'input concentration of acetate')

    S_h2_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>h2</sub><sup> (in)</sup>', description = 'input concentration of hydrogen (liquid)')
    
    X_c_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>c</sub><sup> (in)</sup>', description = 'input concentration of composites')

    X_ch_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>ch</sub><sup> (in)</sup>', description = 'input concentration of carbohydrates')

    X_pr_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>pr</sub><sup> (in)</sup>', description = 'input concentration of proteins')

    X_li_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>li</sub><sup> (in)</sup>', description = 'input concentration of lipids')

    X_su_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>su</sub><sup> (in)</sup>', description = 'input concentration of sugar degraders')

    X_aa_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>aa</sub><sup> (in)</sup>', description = 'input concentration of amino acid degraders')

    X_fa_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>fa</sub><sup> (in)</sup>', description = 'input concentration of LCFA degraders')
        
    inputConcentrationsFG = F.FieldGroup([
            S_su_in, S_aa_in, S_fa_in, S_ac_in, S_h2_in,
            X_c_in, X_ch_in, X_pr_in, X_li_in,X_su_in, X_aa_in, X_fa_in,
        ],
        label = 'Input concentrations (R-H2)'
    )
    
    # Initial concentrations of components
    S_su_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>su</sub><sup> (0)</sup>', description = 'initial concentration of sugars')

    S_aa_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>aa</sub><sup> (0)</sup>', description = 'initial concentration of amino acids')

    S_fa_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>fa</sub><sup> (0)</sup>', description = 'initial concentration of fatty acids (LCFA)')
    
    S_ac_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>ac</sub><sup> (0)</sup>', description = 'initial concentration of acetate')

    S_h2_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>h2</sub><sup> (0)</sup>', description = 'initial concentration of hydrogen (liquid)')
  
    X_c_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>c</sub><sup> (0)</sup>', description = 'initial concentration of composites')
  
    X_ch_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>ch</sub><sup> (0)</sup>', description = 'initial concentration of carbohydrates')
  
    X_pr_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>pr</sub><sup> (0)</sup>', description = 'initial concentration of proteins')

    X_li_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>li</sub><sup> (0)</sup>', description = 'initial concentration of lipids')
     
    X_su_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>su</sub><sup> (0)</sup>', description = 'initial concentration of sugar degraders')
     
    X_aa_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>aa</sub><sup> (0)</sup>', description = 'initial concentration of amino acid degraders')

    X_fa_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'X<sub>fa</sub><sup> (0)</sup>', description = 'initial concentration of LCFA degraders')
   
    S_gas_h2_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'kgCOD/m**3'), minValue = (0, 'kgCOD/m**3'), 
        label = 'S<sub>gas,h2</sub><sup> (0)</sup>', description = 'initial concentration of hydrogen (gas)')

    initialConcentrationsFG = F.FieldGroup([
            S_su_0, S_aa_0, S_fa_0, S_ac_0, S_h2_0,
            X_c_0, X_ch_0, X_pr_0, X_li_0, X_su_0, X_aa_0, X_fa_0,
            S_gas_h2_0,
        ],
        label = 'Initial concentrations (R-H2)'
    )
    
    #1.2 Super groups - parameters & concentrations   
    parametersSG = F.SuperGroup([
            stoichiometricParametersFG, biochemicalParametersFG,
            temperatureParametersFG, physiochemicalParametersFG, 
            physicalParametersFG, volumetricFlowRatesFG,
        ], 
        label = "Parameters (R-H2)"
    )
    
    concentrationsSG = F.SuperGroup([
            initialConcentrationsFG, inputConcentrationsFG,
        ], 
        label = "Concentrations (R-H2)"
    )
    
    modelBlocks = []

class ADM1H2CH4Bioreactors(NumericalModel):
    label = "(H2,CH4) Bioreactors"
    description = F.ModelDescription("A model of two separate contiguous bioreactors for producing of hydrogen and methane, respectively.", show = True)
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show = False) #:TODO: (MILEN)
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    parametersRH2 = F.SubModelGroup(H2Bioreactor, 'parametersSG', label = 'Parameters (R-H2)')
    concentrationsRH2 = F.SubModelGroup(H2Bioreactor, 'concentrationsSG', label = 'Concentrations (R-H2)')
    
    #1.3 Fields - Settings
    solverSettingsRH2 = F.SubModelGroup(SolverSettings, 'FG', label = 'Bioreactor (R-H2)')
    solverSettingsRCH4 = F.SubModelGroup(SolverSettings, 'FG', label = 'Bioreactor (R-CH4)')
    settingsSG = F.SuperGroup([solverSettingsRH2, solverSettingsRCH4], label = 'Solver settings')
    
    #1.4 Model view
    exampleAction = A.ServerAction(
        "loadEg", 
        label = "Examples", 
        options = (
            ('exampleDef', 'Reset to default values'), 
        )
    )
     
    inputView = F.ModelView(
        ioType = "input", 
        superGroups = [parametersRH2, concentrationsRH2, settingsSG], 
        autoFetch = True,
        actionBar = A.ActionBar([exampleAction]),
    )
    
    #2. ############ Results ###############
    varTuples = (
        ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
        ('S_su', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('S_aa', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('S_fa', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('S_ac', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('S_h2', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('X_c', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('X_ch', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('X_pr', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('X_li', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('X_su', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('X_aa', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('X_fa', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('S_gas_h2', F.Quantity('Bio_CODConcentration', default=(1, 'kgCOD/m**3'))),
        ('m_gas_h2', F.Quantity('Bio_Mass', default=(1, 'kgCOD'))),
        ('D', F.Quantity('Bio_TimeRate', default=(1, '1/day'))),
    )
    
    plot = F.PlotView(
        varTuples,
        label='Plot', 
        options = {'ylabel' : None}, 
    )
    table = F.TableView(
        varTuples,
        label='Table', 
        options = {'title': 'Simple Chemostat', 'formats': ['0.000', '0.000', '0.000', '0.000']}
    )
    
    resultsVG = F.ViewGroup([plot, table], label = 'Results')
    resultsSG = F.SuperGroup([resultsVG])
    
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    ############# Methods ###############
    def __init__(self):
        self.exampleDef()
        
    def exampleDef(self):
        #Stoichiometric parameter values
        self.parametersRH2.f_ch_xc = 0.2 #-
        self.parametersRH2.f_pr_xc = 0.2 #-
        self.parametersRH2.f_li_xc = 0.3 #-
        
        self.parametersRH2.f_fa_li = 0.95 #-
        
        self.parametersRH2.f_ac_su = 0.41 #-
        self.parametersRH2.f_h2_su = 0.19 #-
        
        self.parametersRH2.f_ac_aa = 0.4 #-
        self.parametersRH2.f_h2_aa = 0.06 #-
        
        self.parametersRH2.Y_su = 0.1 #-
        self.parametersRH2.Y_aa = 0.08 #-
        self.parametersRH2.Y_fa = 0.06 #-
        
        #Biochemical parameter values
        self.parametersRH2.k_dis = (0.5, '1/day')
        
        self.parametersRH2.k_hyd_ch = (10.0, '1/day')
        self.parametersRH2.k_hyd_pr = (10.0, '1/day')
        self.parametersRH2.k_hyd_li = (10.0, '1/day')
        
        self.parametersRH2.k_m_su = (30.0, '1/day')
        self.parametersRH2.K_S_su = (0.5, 'kgCOD/m**3')
        
        self.parametersRH2.k_m_aa = (50.0, '1/day')
        self.parametersRH2.K_S_aa = (0.3, 'kgCOD/m**3') 
        
        self.parametersRH2.k_m_fa = (6.0, '1/day')
        self.parametersRH2.K_S_fa = (0.4, 'kgCOD/m**3')
        
        self.parametersRH2.k_m_h2 = (35.0, '1/day')
        self.parametersRH2.K_S_h2 = (7.e-6, 'kgCOD/m**3')
        
        # Physiochemical parameter values (Temperatures)
        self.parametersRH2.T_base = (15.0, 'degC')
        self.parametersRH2.T_op = (35.0, 'degC')
    
        # Physiochemical parameter values
        self.parametersRH2.kLa_h2 = (200, '1/day')
        
        # Physical parameter valures
        self.parametersRH2.V_liq = (34.0, 'L')
        self.parametersRH2.V_gas = ( 3.0, 'L')
        
        # Volumetric flow rate values
        self.parametersRH2.q_liq_vals[0] = (10, 1.7*1e-3) #(day, m**3/day)
        self.parametersRH2.q_gas = (30.0, 'L/day')
        
        # Input concentrations 
        self.concentrationsRH2.S_su_in = (0 * 0.01, 'kgCOD/m**3')
        self.concentrationsRH2.S_aa_in = (0 * 0.001, 'kgCOD/m**3')
        self.concentrationsRH2.S_fa_in = (0 * 0.001, 'kgCOD/m**3')
        self.concentrationsRH2.S_ac_in = (0 * 0.001, 'kgCOD/m**3')
        self.concentrationsRH2.S_h2_in = (0 * 1e-8, 'kgCOD/m**3')
        self.concentrationsRH2.X_c_in = (2.0, 'kgCOD/m**3')
        self.concentrationsRH2.X_ch_in = (5.0, 'kgCOD/m**3')
        self.concentrationsRH2.X_pr_in = (20.0, 'kgCOD/m**3')
        self.concentrationsRH2.X_li_in = (5.0, 'kgCOD/m**3')
        self.concentrationsRH2.X_su_in = (0 * 0.01, 'kgCOD/m**3')
        self.concentrationsRH2.X_aa_in = (0 * 0.01, 'kgCOD/m**3')
        self.concentrationsRH2.X_fa_in = (0 * 0.01, 'kgCOD/m**3')
        self.concentrationsRH2.S_gas_h2_in = (0 * 1e-5, 'kgCOD/m**3')
        
        # Initial values of state variables 
        self.concentrationsRH2.S_su_0 = (0.012, 'kgCOD/m**3')
        self.concentrationsRH2.S_aa_0 = (0.005, 'kgCOD/m**3')
        self.concentrationsRH2.S_fa_0 = (0.099, 'kgCOD/m**3')
        self.concentrationsRH2.S_ac_0 = (0.20, 'kgCOD/m**3')
        self.concentrationsRH2.S_h2_0 = (2.4e-7, 'kgCOD/m**3')
        self.concentrationsRH2.X_c_0 = (0.31, 'kgCOD/m**3')
        self.concentrationsRH2.X_ch_0 = (0.028, 'kgCOD/m**3')
        self.concentrationsRH2.X_pr_0 = (0.10, 'kgCOD/m**3')
        self.concentrationsRH2.X_li_0 = (0.03, 'kgCOD/m**3')
        self.concentrationsRH2.X_su_0 = (0.42, 'kgCOD/m**3')
        self.concentrationsRH2.X_aa_0 = (1.18, 'kgCOD/m**3')
        self.concentrationsRH2.X_fa_0 = (0.24, 'kgCOD/m**3')
        self.concentrationsRH2.S_gas_h2_0 = (1e-5, 'kgCOD/m**3')
        
        # Solver settings
        self.solverSettingsRH2.tFinal = (50.0, 'day')
        self.solverSettingsRH2.tPrint = (0.025, 'day')
                        
    def compute(self):
        bioreactor = DM.ADM1H2Bioreactor(self.parametersRH2, self.concentrationsRH2)
        
        bioreactor.prepareSimulation()
        bioreactor.run(self.solverSettingsRH2)
        
        res = bioreactor.getResults()
        results = np.array(res)
        self.plot = results
        self.table = results
    
