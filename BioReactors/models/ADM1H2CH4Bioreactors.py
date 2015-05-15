'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.model.fields as F
import smo.model.actions as A 
import smo.dynamical_models.bioreactors.ADM1H2Bioreactor as DM_RH2
import smo.dynamical_models.bioreactors.ADM1CH4Bioreactor as DM_RCH4

from smo.model.model import NumericalModel
#from smo.web.modules import RestModule

class SolverSettings(NumericalModel):
    tFinal = F.Quantity('Bio_Time', default = (0., 'day'), minValue = (0, 'day'), maxValue=(1000, 'day'), label = 'simulation time')
    tPrint = F.Quantity('Bio_Time', default = (0., 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval')
    
    FG = F.FieldGroup([tFinal, tPrint], label = 'Solver')
    SG = F.SuperGroup([FG], label = 'Settings')
    
    modelBlocks = []
    
class CH4Bioreactor(NumericalModel):
    # Stoichiometric parameter values
    Y_ac = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>ac</sub>', description = 'yield of acetate degraders on acetate')
    
    stoichiometricParametersFG = F.FieldGroup([
            Y_ac,
        ],
        label = 'Stoichiometric parameters (R-CH4)'
    )
    
    # Biochemical parameter values
    k_m_ac = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,ac</sub>', description = 'specific Monod maximum uptake rate of acetate degraders')
    K_S_ac = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'K<sub>S,ac</sub>', description = 'Monod half saturation constant of acetate degraders')
  
    
    biochemicalParametersFG = F.FieldGroup([
            k_m_ac, K_S_ac, 
        ],
        label = 'Biochemical parameters (R-CH4)'
    )
    
    # Physiochemical parameters (Temperatures)
    T_base = F.Quantity('Temperature', default = (0.0, 'degC'),
        label = 'T<sub>base</sub>', description = 'base (ambient) temperature')
    T_op = F.Quantity('Temperature', default = (0.0, 'degC'),
        label = 'T<sub>op</sub>', description = 'operating temperature')
    
    temperatureParametersFG = F.FieldGroup([
            T_base, T_op,
        ],
        label = 'Temperatures (R-CH4)'
    )
    
    # Physiochemical parameters
    kLa_ch4 = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>L</sub>a<sub> ch4</sub>', description = 'gas-liquid transfer coefficient of methane')

    physiochemicalParametersFG = F.FieldGroup([
           kLa_ch4,
        ],
        label = 'Physiochemical parameters (R-CH4)'
    )

    # Physical parameters
    V_liq_del_V_gas = F.Quantity(default = 0.0,
        label = 'V<sub>liq</sub>/V<sub>gas</sub>', description = 'fraction between the volume of the liquid part and the volume of the gas headspace of the reactor')
    
    physicalParametersFG = F.FieldGroup([
            V_liq_del_V_gas,
        ],
        label = 'Physical parameters (R-CH4)'
    )
    
    # Volumetri flow rates
    D_liq_vals = F.RecordArray(
        (
            ('time', F.Quantity('Bio_Time', default = (10.0, 'day'), minValue = (0, 'day'), label = 'Duration')),
            ('D', F.Quantity('Bio_TimeRate', default = (1.0, '1/day'), minValue = (0, '1/day'), label = 'dilution rate')),
        ), 
        label = 'D<sub> liq</sub>', 
        description = 'liquid dilution (or washout) rate',
        toggle = True,
    ) 
    
    D_gas = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'D<sub> gas</sub>', description = 'gas dilution (or washout) rate')

    dilutionRatesFG = F.FieldGroup([
            D_liq_vals, D_gas
        ],
        label = 'Dilution rates (R-CH4)'
    )
    
    # Input concentrations of components
    S_ac_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>ac</sub><sup> (in)</sup>', description = 'input concentration of acetate')
    
    S_ch4_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>ch4</sub><sup> (in)</sup>', description = 'input concentration of methane')

    X_ac_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>ac</sub><sup> (in)</sup>', description = 'input concentration of acetate degraders')

    inputConcentrationsFG = F.FieldGroup([
            S_ac_in, S_ch4_in,
            X_ac_in, 
        ],
        label = 'Input concentrations (R-CH4)'
    )
    
    # Initial concentrations of components
    S_ac_from_RH2 = F.Boolean(True, 
        label = 'S<sub>ac</sub> <sup>(0)</sup> = S<sub>ac</sub><sup>(R-H2)</sup>', description = 'take the inital acetate concentration from the H2 Bioreactor (R-H2)')
    
    S_ac_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>ac</sub><sup> (0)</sup>', description = 'initial concentration of acetate', 
        show = 'self.S_ac_from_RH2 == false')

    S_ch4_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>ch4</sub><sup> (0)</sup>', description = 'initial concentration of methane (liquid)')
    
    X_ac_0 = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>ac</sub><sup> (0)</sup>', description = 'initial concentration of acetate degraders')
   
    S_gas_ch4_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>gas,ch4</sub><sup> (0)</sup>', description = 'initial concentration of methane (gas)')

    initialConcentrationsFG = F.FieldGroup([
            S_ac_from_RH2, 
            S_ac_0, S_ch4_0,
            X_ac_0,
            S_gas_ch4_0,
        ],
        label = 'Initial concentrations (R-CH4)'
    )
    
    #1.2 Super groups - parameters & concentrations   
    parametersSG = F.SuperGroup([
            stoichiometricParametersFG, biochemicalParametersFG,
            temperatureParametersFG, physiochemicalParametersFG, 
            physicalParametersFG, dilutionRatesFG,
        ], 
        label = "Parameters (R-CH4)"
    )
    
    concentrationsSG = F.SuperGroup([
            initialConcentrationsFG, inputConcentrationsFG,
        ], 
        label = "Concentrations (R-CH4)"
    )
    
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
    K_S_su = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'K<sub>S,su</sub>', description = 'Monod half saturation constant of sugar degraders')
    
    k_m_aa = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,aa</sub>', description = 'specific Monod maximum uptake rate of amino acids degraders')
    K_S_aa = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'K<sub>S,aa</sub>', description = 'Monod half saturation constant of amino acids degraders')
    
    k_m_fa = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,fa</sub>', description = 'specific Monod maximum uptake rate of LCFA degraders')
    K_S_fa = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
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
    V_liq_del_V_gas = F.Quantity(default = 0.0,
        label = 'V<sub>liq</sub>/V<sub>gas</sub>', 
        description = 'fraction between the volume of the liquid part and the volume of the gas headspace of the reactor')

    physicalParametersFG = F.FieldGroup([
            V_liq_del_V_gas,
        ],
        label = 'Physical parameters (R-H2)'
    )
    
    # Dilution rates
    D_liq_vals = F.RecordArray(
        (
            ('time', F.Quantity('Bio_Time', default = (10.0, 'day'), minValue = (0, 'day'), label = 'Duration')),
            ('D', F.Quantity('Bio_TimeRate', default = (1.0, '1/day'), minValue = (0, '1/day'), label = 'dilution rate')),
        ), 
        label = 'D<sub> liq</sub>', 
        description = 'liquid dilution (or washout) rate',
        toggle = True,
    ) 
    
    D_gas = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'D<sub> gas</sub>', description = 'gas dilution (or washout) rate')

    dilutionRatesFG = F.FieldGroup([
            D_liq_vals, D_gas
        ],
        label = 'Dilution rates (R-H2)'
    )
    
    # Input concentrations of components
    S_su_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>su</sub><sup> (in)</sup>', description = 'input concentration of sugars')

    S_aa_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>aa</sub><sup> (in)</sup>', description = 'input concentration of amino acids')

    S_fa_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>fa</sub><sup> (in)</sup>', description = 'input concentration of fatty acids (LCFA)')

    S_ac_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>ac</sub><sup> (in)</sup>', description = 'input concentration of acetate')

    S_h2_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>h2</sub><sup> (in)</sup>', description = 'input concentration of hydrogen (liquid)')
    
    X_c_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>c</sub><sup> (in)</sup>', description = 'input concentration of composites')

    X_ch_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>ch</sub><sup> (in)</sup>', description = 'input concentration of carbohydrates')

    X_pr_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>pr</sub><sup> (in)</sup>', description = 'input concentration of proteins')

    X_li_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>li</sub><sup> (in)</sup>', description = 'input concentration of lipids')

    X_su_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>su</sub><sup> (in)</sup>', description = 'input concentration of sugar degraders')

    X_aa_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>aa</sub><sup> (in)</sup>', description = 'input concentration of amino acid degraders')

    X_fa_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>fa</sub><sup> (in)</sup>', description = 'input concentration of LCFA degraders')
        
    inputConcentrationsFG = F.FieldGroup([
            S_su_in, S_aa_in, S_fa_in, S_ac_in, S_h2_in,
            X_c_in, X_ch_in, X_pr_in, X_li_in,X_su_in, X_aa_in, X_fa_in,
        ],
        label = 'Input concentrations (R-H2)'
    )
    
    # Initial concentrations of components
    S_su_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>su</sub><sup> (0)</sup>', description = 'initial concentration of sugars')

    S_aa_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>aa</sub><sup> (0)</sup>', description = 'initial concentration of amino acids')

    S_fa_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>fa</sub><sup> (0)</sup>', description = 'initial concentration of fatty acids (LCFA)')
    
    S_ac_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>ac</sub><sup> (0)</sup>', description = 'initial concentration of acetate')

    S_h2_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>h2</sub><sup> (0)</sup>', description = 'initial concentration of hydrogen (liquid)')
  
    X_c_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>c</sub><sup> (0)</sup>', description = 'initial concentration of composites')
  
    X_ch_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>ch</sub><sup> (0)</sup>', description = 'initial concentration of carbohydrates')
  
    X_pr_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>pr</sub><sup> (0)</sup>', description = 'initial concentration of proteins')

    X_li_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>li</sub><sup> (0)</sup>', description = 'initial concentration of lipids')
     
    X_su_0 = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>su</sub><sup> (0)</sup>', description = 'initial concentration of sugar degraders')
     
    X_aa_0 = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>aa</sub><sup> (0)</sup>', description = 'initial concentration of amino acid degraders')

    X_fa_0 = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>fa</sub><sup> (0)</sup>', description = 'initial concentration of LCFA degraders')
   
    S_gas_h2_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
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
            physicalParametersFG, dilutionRatesFG,
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
    figure = F.ModelFigure(src="BioReactors/img/ModuleImages/SimpleChemostat.png", show = False) #:TODO: (MILEN) ADM1H2CH4Bioreactors png
    
    async = True
    progressOptions = {'suffix': 'day', 'fractionOutput': True}
    
    #1. ############ Inputs ###############
    #1.1 Fields - Input values
    parametersRH2 = F.SubModelGroup(H2Bioreactor, 'parametersSG', label = 'Parameters (R-H2)')
    concentrationsRH2 = F.SubModelGroup(H2Bioreactor, 'concentrationsSG', label = 'Concentrations (R-H2)')
    
    parametersRCH4 = F.SubModelGroup(CH4Bioreactor, 'parametersSG', label = 'Parameters (R-CH4)')
    concentrationsRCH4 = F.SubModelGroup(CH4Bioreactor, 'concentrationsSG', label = 'Concentrations (R-CH4)')
    
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
        superGroups = [parametersRH2, concentrationsRH2, parametersRCH4, concentrationsRCH4, settingsSG], 
        autoFetch = True,
        actionBar = A.ActionBar([exampleAction]),
    )
    
    #2. ############ Results (R-H2) ###############
    storageRH2 = F.HdfStorage(hdfFile = DM_RH2.dataStorageFilePath, hdfGroup = DM_RH2.dataStorageDatasetPath)
    
    varTuplesRH2 = (
        ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
        ('S_su', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('S_aa', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('S_fa', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('S_ac', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('S_h2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('X_c', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('X_ch', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('X_pr', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('X_li', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('X_su', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('X_aa', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('X_fa', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('S_gas_h2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('m_gas_h2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('D', F.Quantity('Bio_TimeRate', default=(1, '1/day'))),
    )
    
    plotRH2 = F.PlotView(
        varTuplesRH2,
        label='Plot', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 4, 6, 13],
        useHdfStorage = True,
        storage = 'storageRH2',
    )
    tableRH2 = F.TableView(
        varTuplesRH2,
        label='Table', 
        options = {'title': 'H2 Bioreactor', 'formats': ['0.000', '0.000', '0.000', '0.000']},
        useHdfStorage = True,
        storage = 'storageRH2',
    )
    
    storageRH2VG = F.ViewGroup([storageRH2], show="false")
    resultsRH2VG = F.ViewGroup([plotRH2, tableRH2])
    resultsRH2SG = F.SuperGroup([resultsRH2VG, storageRH2VG], label = 'Results (R-H2)')
    
    #2. ############ Results (R-CH4) ###############
    storageRCH4 = F.HdfStorage(hdfFile = DM_RCH4.dataStorageFilePath, hdfGroup = DM_RCH4.dataStorageDatasetPath)
    
    varTuplesRCH4 = (
        ('time', F.Quantity('Bio_Time', default=(1, 'day'))),
        ('S_ac', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('S_ch4', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('X_ac', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))),
        ('S_gas_ch4', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('m_gas_ch4', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))),
        ('D', F.Quantity('Bio_TimeRate', default=(1, '1/day'))),
    )
    
    plotRCH4 = F.PlotView(
        varTuplesRCH4,
        label='Plot', 
        options = {'ylabel' : None},
        visibleColumns = [0, 1, 2, 4],
        useHdfStorage = True,
        storage = 'storageRCH4',
    )
    tableRCH4 = F.TableView(
        varTuplesRCH4,
        label='Table', 
        options = {'title': 'CH4 Bioreactor', 'formats': ['0.000', '0.000', '0.000', '0.000']},
        useHdfStorage = True,
        storage = 'storageRCH4',
    )
    
    storageRCH4VG = F.ViewGroup([storageRCH4], show="false")
    resultsRCH4VG = F.ViewGroup([plotRCH4, tableRCH4])
    resultsRCH4SG = F.SuperGroup([resultsRCH4VG, storageRCH4VG], label = 'Results (R-CH4)')
    
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsRH2SG, resultsRCH4SG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    ############# Methods ###############
    def __init__(self):
        self.exampleDef()
        
    def exampleDef(self):
        ############# H2 Bioreactor ###############
        #Stoichiometric parameter values
        self.parametersRH2.f_ch_xc = 0.5 #-
        self.parametersRH2.f_pr_xc = 0.15 #-
        self.parametersRH2.f_li_xc = 0.15 #-
        
        self.parametersRH2.f_fa_li = 0.9 #-
        
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
        self.parametersRH2.K_S_su = (0.5, 'g/L')
        
        self.parametersRH2.k_m_aa = (50.0, '1/day')
        self.parametersRH2.K_S_aa = (0.3, 'g/L') 
        
        self.parametersRH2.k_m_fa = (6.0, '1/day')
        self.parametersRH2.K_S_fa = (0.4, 'g/L')
        
        # Physiochemical parameter values (Temperatures)
        self.parametersRH2.T_base = (15.0, 'degC')
        self.parametersRH2.T_op = (35.0, 'degC')
    
        # Physiochemical parameter values
        self.parametersRH2.kLa_h2 = (200, '1/day')
        
        # Physical parameter valures
        self.parametersRH2.V_liq_del_V_gas = 3.0 #L/L
        
        # Volumetric flow rate values
        self.parametersRH2.D_liq_vals[0] = (10, 0.0) #(day, 1/day)
        self.parametersRH2.D_gas = (1.0, '1/day')
        
        # Input concentrations 
        self.concentrationsRH2.S_su_in = (0, 'gCOD/L')
        self.concentrationsRH2.S_aa_in = (0, 'gCOD/L')
        self.concentrationsRH2.S_fa_in = (0, 'gCOD/L')
        self.concentrationsRH2.S_ac_in = (0, 'gCOD/L')
        self.concentrationsRH2.S_h2_in = (0, 'gCOD/L')
        self.concentrationsRH2.X_c_in = (2.0, 'gCOD/L')
        self.concentrationsRH2.X_ch_in = (0, 'gCOD/L')
        self.concentrationsRH2.X_pr_in = (0, 'gCOD/L')
        self.concentrationsRH2.X_li_in = (0, 'gCOD/L')
        self.concentrationsRH2.X_su_in = (0, 'g/L')
        self.concentrationsRH2.X_aa_in = (0, 'g/L')
        self.concentrationsRH2.X_fa_in = (0, 'g/L')
        self.concentrationsRH2.S_gas_h2_in = (0, 'gCOD/L')
        
        # Initial values of state variables 
        self.concentrationsRH2.S_su_0 = (0.012, 'gCOD/L')
        self.concentrationsRH2.S_aa_0 = (0.005, 'gCOD/L')
        self.concentrationsRH2.S_fa_0 = (0.099, 'gCOD/L')
        self.concentrationsRH2.S_ac_0 = (0.20, 'gCOD/L')
        self.concentrationsRH2.S_h2_0 = (2.4e-7, 'gCOD/L')
        self.concentrationsRH2.X_c_0 = (30, 'gCOD/L')
        self.concentrationsRH2.X_ch_0 = (0.028, 'gCOD/L')
        self.concentrationsRH2.X_pr_0 = (0.10, 'gCOD/L')
        self.concentrationsRH2.X_li_0 = (0.03, 'gCOD/L')
        self.concentrationsRH2.X_su_0 = (0.42, 'g/L')
        self.concentrationsRH2.X_aa_0 = (1.18, 'g/L')
        self.concentrationsRH2.X_fa_0 = (0.24, 'g/L')
        self.concentrationsRH2.S_gas_h2_0 = (1e-5, 'gCOD/L')
        
        # Solver settings
        self.solverSettingsRH2.tFinal = (10.0, 'day')
        self.solverSettingsRH2.tPrint = (0.01, 'day')
        
        
        ############# CH4 Bioreactor ###############
        #Stoichiometric parameter values
        self.parametersRCH4.Y_ac = 0.5 #-
        
        #Biochemical parameter values
        self.parametersRCH4.k_m_ac = (8.0, '1/day')
        self.parametersRCH4.K_S_ac = (0.15, 'g/L') 

        # Physiochemical parameter values (Temperatures)
        self.parametersRCH4.T_base = (15.0, 'degC')
        self.parametersRCH4.T_op = (35.0, 'degC')
    
        # Physiochemical parameter values
        self.parametersRCH4.kLa_ch4 = (200, '1/day')
        
        # Physical parameter valures
        self.parametersRCH4.D_liq_vals[0] = (10, 1.0) #(day, 1/day)
        self.parametersRCH4.D_gas = (1.0, '1/day')

        # Input concentrations 
        self.concentrationsRCH4.S_ac_in = (0.44, 'gCOD/L')
        self.concentrationsRCH4.S_ch4_in = (0, 'gCOD/L')
        self.concentrationsRCH4.X_ac_in = (0, 'g/L')
        
        # Initial values of state variables 
        self.concentrationsRCH4.S_ac_0 = (0.2, 'gCOD/L')
        self.concentrationsRCH4.S_ch4_0 = (1e-5, 'gCOD/L')
        self.concentrationsRCH4.X_ac_0 = (2, 'g/L')
        self.concentrationsRCH4.S_gas_ch4_0 = (1e-5, 'gCOD/L')
        
        # Solver settings
        self.solverSettingsRCH4.tFinal = (2.0, 'day')
        self.solverSettingsRCH4.tPrint = (0.01, 'day')
                    
    def computeAsync(self):
        # Simulate R-H2 Bioreactor
        bioreactorRH2 = DM_RH2.ADM1H2Bioreactor(self, self.parametersRH2, self.concentrationsRH2)
        
        bioreactorRH2.prepareSimulation()
        bioreactorRH2.run(self.solverSettingsRH2)
        
        # Show results R-H2 Bioreactor
        self.storageRH2 = bioreactorRH2.resultStorage.simulationName
        
        
        # Connnect the two bioreactors
        if self.concentrationsRCH4.S_ac_from_RH2:
            self.concentrationsRCH4.S_ac_0 = 10.0 #:TODO: (Milen) resultsRH2['S_ac'][-1]
     
     
        # Simulate R-CH4 Bioreactor
        bioreactorRCH4 = DM_RCH4.ADM1CH4Bioreactor(self, self.parametersRCH4, self.concentrationsRCH4)
         
        bioreactorRCH4.prepareSimulation()
        bioreactorRCH4.run(self.solverSettingsRCH4)
         
        # Show results R-CH4 Bioreactor
        self.storageRCH4 = bioreactorRCH4.resultStorage.simulationName
