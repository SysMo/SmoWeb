'''
Created on Mar 4, 2015

@author: Milen Borisov
@copyright: SysMo Ltd, Bulgaria
'''
import smo.model.fields as F
import smo.model.actions as A 
import smo.dynamical_models.bioreactors.ADM1H2CH4Bioreactors as DM

from smo.model.model import NumericalModel
#from smo.web.modules import RestModule

class SolverSettings(NumericalModel):
    tFinal = F.Quantity('Bio_Time', default = (0.0, 'day'), minValue = (0, 'day'), maxValue=(1000, 'day'), label = 'simulation time')
    tPrint = F.Quantity('Bio_Time', default = (0.0, 'day'), minValue = (1e-5, 'day'), maxValue = (100, 'day'), label = 'print interval')
    
    absTol = F.Quantity('Bio_Time', default = (0.0, 'day'), minValue = (1e-16, 'day'), maxValue = (1e-5, 'day'), label = 'absolute tolerance')
    relTol = F.Quantity('Bio_Time', default = (0.0, 'day'), minValue = (1e-16, 'day'), maxValue = (1e-3, 'day'), label = 'relative tolerance')
    
    FG = F.FieldGroup([tFinal, tPrint, absTol, relTol], label = 'Solver')
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
    
    # Physiochemical parameters
    Y_ch4_ac = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>ch4,ac</sub>', description = 'yield coefficient of methane on acetate')

    physiochemicalParametersFG = F.FieldGroup([
           Y_ch4_ac
        ],
        label = 'Physiochemical parameters (R-CH4)'
    )

    # Physical parameters
    V_liq_RCH4_del_V_liq_RH2 = F.Quantity(default = (0.0, '-'),
        label = 'V<sub>liq,RCH4</sub>/V<sub>liq,RH2</sub>', description = 'fraction between the volume of the liquid part of the H2 and CH4 bioreactors')
    
    
    physicalParametersFG = F.FieldGroup([
            V_liq_RCH4_del_V_liq_RH2
        ],
        label = 'Physical parameters (R-CH4)'
    )
    
    # Input concentrations of components
    X_ac_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>ac</sub><sup> (in)</sup>', description = 'input concentration of acetate degraders')

    inputConcentrationsFG = F.FieldGroup([
            X_ac_in, 
        ],
        label = 'Input concentrations (R-CH4)'
    )
    
    # Initial concentrations of components
    S_ac_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'S<sub>ac</sub><sup> (0)</sup>', description = 'initial concentration of acetate')

    X_ac_0 = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>ac</sub><sup> (0)</sup>', description = 'initial concentration of acetate degraders')

    initialConcentrationsFG = F.FieldGroup([
            S_ac_0,
            X_ac_0,
        ],
        label = 'Initial concentrations (R-CH4)'
    )
    
    #1.2 Super groups - parameters & concentrations   
    parametersSG = F.SuperGroup([
            stoichiometricParametersFG, biochemicalParametersFG,
            physiochemicalParametersFG, physicalParametersFG,
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
    
    f_su_li = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>su,li</sub>', description = 'yield of sugar on lipids')
    f_fa_li = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>fa,li</sub>', description = 'yield of LCFA on lipids')
    
    f_ac_su = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>ac,su</sub>', description = 'yield of acetate on sugars')
    
    f_ac_aa = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'f<sub>ac,aa</sub>', description = 'yield of acetate on amino acids')
    
    Y_suaa = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>su-aa</sub>', description = 'yield of sugar and amino acid degraders on sugars and amino acids')
    Y_fa = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>fa</sub>', description = 'yield of LCFA degraders on LCFA')
    
    stoichiometricParametersFG = F.FieldGroup([
            f_ch_xc, f_pr_xc, f_li_xc, f_su_li, f_fa_li, f_ac_su,
            f_ac_aa, Y_suaa, Y_fa
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
    
    k_m_suaa = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,su-aa</sub>', description = 'specific Monod maximum uptake rate of sugar and amino acids degraders')
    K_S_suaa = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'K<sub>S,su-aa</sub>', description = 'Monod half saturation constant of sugar and amino acids degraders')
    
    k_m_fa = F.Quantity('Bio_TimeRate', default = (0.0, '1/day'), minValue = (0, '1/day'), 
        label = 'k<sub>m,fa</sub>', description = 'specific Monod maximum uptake rate of LCFA degraders')
    K_S_fa = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'K<sub>S,fa</sub>', description = 'Monod half saturation constant of LCFA degraders')
    
    biochemicalParametersFG = F.FieldGroup([
            k_dis, k_hyd_ch, k_hyd_pr, k_hyd_li,
            k_m_suaa, K_S_suaa, k_m_fa, K_S_fa, 
        ],
        label = 'Biochemical parameters (R-H2)'
    )
    
    # Physiochemical parameters
    Y_h2_su = F.Quantity(default = 0.0, minValue = 0.0,
        label = 'Y<sub>h2,su</sub>', description = 'yield coefficient of hydrogen on sugar')

    Y_h2_aa = F.Quantity(default = 0.0, minValue = 0.0,
            label = 'Y<sub>h2,aa</sub>', description = 'yield coefficient of hydrogen on amino acids')
    
    Y_h2_fa = F.Quantity(default = 0.0, minValue = 0.0,
            label = 'Y<sub>h2,fa</sub>', description = 'yield coefficient of hydrogen on LCFA')

    physiochemicalParametersFG = F.FieldGroup([
           Y_h2_su, Y_h2_aa, Y_h2_fa
        ],
        label = 'Physiochemical parameters (R-H2)'
    )
    
    # Dilution rates
    D_liq_arr = F.RecordArray(
        (
            ('time', F.Quantity('Bio_Time', default = (10.0, 'day'), minValue = (0, 'day'), label = 'Duration')),
            ('D', F.Quantity('Bio_TimeRate', default = (1.0, '1/day'), minValue = (0, '1/day'), label = 'dilution rate')),
        ), 
        label = 'D<sub> liq</sub>', 
        description = 'liquid dilution (or washout) rate',
        numRows = 4,
        toggle = True,
    ) 
    
    dilutionRatesFG = F.FieldGroup([
            D_liq_arr,
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
 
    X_c_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>c</sub><sup> (in)</sup>', description = 'input concentration of composites')

    X_ch_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>ch</sub><sup> (in)</sup>', description = 'input concentration of carbohydrates')

    X_pr_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>pr</sub><sup> (in)</sup>', description = 'input concentration of proteins')

    X_li_in = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>li</sub><sup> (in)</sup>', description = 'input concentration of lipids')

    X_suaa_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>su-aa</sub><sup> (in)</sup>', description = 'input concentration of sugar and amino acids degraders')

    X_fa_in = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>fa</sub><sup> (in)</sup>', description = 'input concentration of LCFA degraders')
        
    inputConcentrationsFG = F.FieldGroup([
            S_su_in, S_aa_in, S_fa_in, S_ac_in,
            X_c_in, X_ch_in, X_pr_in, X_li_in,X_suaa_in, X_fa_in,
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

    X_c_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>c</sub><sup> (0)</sup>', description = 'initial concentration of composites')
  
    X_ch_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>ch</sub><sup> (0)</sup>', description = 'initial concentration of carbohydrates')
  
    X_pr_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>pr</sub><sup> (0)</sup>', description = 'initial concentration of proteins')

    X_li_0 = F.Quantity('Bio_CODConcentration', default = (0.0, 'gCOD/L'), minValue = (0, 'gCOD/L'), 
        label = 'X<sub>li</sub><sup> (0)</sup>', description = 'initial concentration of lipids')
     
    X_suaa_0 = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>su-aa</sub><sup> (0)</sup>', description = 'initial concentration of sugar and amino acids degraders')
     
    X_fa_0 = F.Quantity('Bio_MassConcentration', default = (0.0, 'g/L'), minValue = (0, 'g/L'), 
        label = 'X<sub>fa</sub><sup> (0)</sup>', description = 'initial concentration of LCFA degraders')
   
    initialConcentrationsFG = F.FieldGroup([
            S_su_0, S_aa_0, S_fa_0, S_ac_0,
            X_c_0, X_ch_0, X_pr_0, X_li_0, X_suaa_0, X_fa_0,
        ],
        label = 'Initial concentrations (R-H2)'
    )
    
    #1.2 Super groups - parameters & concentrations   
    parametersSG = F.SuperGroup([
            stoichiometricParametersFG, biochemicalParametersFG,
            physiochemicalParametersFG, dilutionRatesFG,
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
    description = F.ModelDescription("A model of two separate contiguous bioreactors for hydrogen and methane prodoction, respectively.", show = True)
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
    solverSettings = F.SubModelGroup(SolverSettings, 'FG', label = 'H2 & CH4 - Bioreactors')
    settingsSG = F.SuperGroup([solverSettings], label = 'Solver settings')
    
    #1.4 Model view
    exampleAction = A.ServerAction(
        "loadEg", 
        label = "Examples", 
        options = (
            ('exampleDef', 'Reset to default values'),
            ('exampleADM1', 'Reset to ADM1 values'),  
        )
    )
     
    inputView = F.ModelView(
        ioType = "input", 
        superGroups = [parametersRH2, concentrationsRH2, parametersRCH4, concentrationsRCH4, settingsSG], 
        autoFetch = True,
        actionBar = A.ActionBar([exampleAction]),
    )
    
    #2. ############ Results ###############
    storage = F.HdfStorage(hdfFile = DM.dataStorageFilePath, hdfGroup = DM.dataStorageDatasetPath)
    
    varTuples = (
        ('time', F.Quantity('Bio_Time', default=(1, 'day'))), #0
        ('S_su_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #1
        ('S_aa_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #2
        ('S_fa_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #3
        ('S_ac_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #4
        ('X_c_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #5
        ('X_ch_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #6
        ('X_pr_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #7
        ('X_li_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #8
        ('X_suaa_RH2', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))), #9
        ('X_fa_RH2', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))), #10
        ('intQ_h2_RH2', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #11
        
        ('S_ac_RCH4', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #12   
        ('X_ac_RCH4', F.Quantity('Bio_MassConcentration', default=(1, 'g/L'))), #13
        ('intQ_ch4_RCH4', F.Quantity('Bio_CODConcentration', default=(1, 'gCOD/L'))), #14
        
        ('Q_h2_RH2', F.Quantity('Bio_CODConcentrationFlowRate', default=(1, 'gCOD/L/day'))), #15
        ('Q_ch4_RCH4', F.Quantity('Bio_CODConcentrationFlowRate', default=(1, 'gCOD/L/day'))), #16
        
        ('D_RH2', F.Quantity('Bio_TimeRate', default=(1, '1/day'))), #17
        ('D_RCH4', F.Quantity('Bio_TimeRate', default=(1, '1/day'))), #18
    )
    
    plot1RH2 = F.PlotView(
        varTuples,
        label='R-H2 (S<sub>su</sub>, S<sub>aa</sub>, S<sub>fa</sub>)', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 1, 2, 3],
        useHdfStorage = True,
        storage = 'storage',
    )
    
    plot2RH2 = F.PlotView(
        varTuples,
        label='R-H2 (X<sub>ch</sub>, X<sub>pr</sub>, X<sub>li</sub>)', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 6, 7, 8],
        useHdfStorage = True,
        storage = 'storage',
    )
    
    plot3RH2 = F.PlotView(
        varTuples,
        label='R-H2 (X<sub>su-aa</sub>,X<sub>fa</sub>)', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 9, 10],
        useHdfStorage = True,
        storage = 'storage',
    )
    
    plot4RH2 = F.PlotView(
        varTuples,
        label='R-H2 (H<sub>2</sub>)', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 11, 15],
        useHdfStorage = True,
        storage = 'storage',
    )
    
    plot1RCH4 = F.PlotView(
        varTuples,
        label='R-CH4 (S<sub>ac</sub>, X<sub>ac</sub>)', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 12, 13],
        useHdfStorage = True,
        storage = 'storage',
    )

    plot2RCH4 = F.PlotView(
        varTuples,
        label='R-CH4 (CH<sub>4</sub>)', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 14, 16],
        useHdfStorage = True,
        storage = 'storage',
    )
        
    plotD = F.PlotView(
        varTuples,
        label='(D<sub>RH2</sub>, D<sub>RCH4</sub>)', 
        options = {'ylabel' : None}, 
        visibleColumns = [0, 17, 18],
        useHdfStorage = True,
        storage = 'storage',
    )
    
    table = F.TableView(
        varTuples,
        label='Table', 
        options = {'title': 'Bioreactors', 'formats': ['0.000']},
        useHdfStorage = True,
        storage = 'storage',
    )
    
    storageVG = F.ViewGroup([storage], show="false")
    resultsVG = F.ViewGroup([plot1RH2, plot2RH2, plot3RH2, plot4RH2, plot1RCH4, plot2RCH4, plotD, table])
    resultsSG = F.SuperGroup([resultsVG, storageVG], label = 'Results')
    
 
    #2.1 Model view
    resultView = F.ModelView(ioType = "output", superGroups = [resultsSG])
    
    ############# Page structure ########
    modelBlocks = [inputView, resultView]
    
    ############# Methods ###############
    def __init__(self):
        self.exampleADM1()
        
    def exampleDef(self):
        ############# H2 Bioreactor ###############
        #Stoichiometric parameter values
        self.parametersRH2.f_ch_xc = 0.5 #-
        self.parametersRH2.f_pr_xc = 0.15 #-
        self.parametersRH2.f_li_xc = 0.15 #-
        
        self.parametersRH2.f_su_li = 0.05 #-
        self.parametersRH2.f_fa_li = 0.9 #-
        
        self.parametersRH2.f_ac_su = 0.41 #-
        
        self.parametersRH2.f_ac_aa = 0.4 #-
        
        self.parametersRH2.Y_suaa = 0.1 #-
        self.parametersRH2.Y_fa = 0.06 #-
        
        #Biochemical parameter values
        self.parametersRH2.k_dis = (0.5, '1/day')
        
        self.parametersRH2.k_hyd_ch = (10.0, '1/day')
        self.parametersRH2.k_hyd_pr = (10.0, '1/day')
        self.parametersRH2.k_hyd_li = (10.0, '1/day')
        
        self.parametersRH2.k_m_suaa = (30.0, '1/day')
        self.parametersRH2.K_S_suaa = (0.5, 'g/L')
        
        self.parametersRH2.k_m_fa = (6.0, '1/day')
        self.parametersRH2.K_S_fa = (0.4, 'g/L')
    
        # Physiochemical parameter values
        self.parametersRH2.Y_h2_su = 1.0 #-
        self.parametersRH2.Y_h2_aa = 1.0 #-
        self.parametersRH2.Y_h2_fa = 1.0 #-
        
        # Volumetric flow rate values
        self.parametersRH2.D_liq_arr[0] = (10.0, 0.0) #(day, 1/day)
        self.parametersRH2.D_liq_arr[1] = (10.0, 0.1) #(day, 1/day)
        self.parametersRH2.D_liq_arr[2] = (10.0, 0.05) #(day, 1/day)
        self.parametersRH2.D_liq_arr[3] = (10.0, 0.15) #(day, 1/day)
        
        # Input concentrations 
        self.concentrationsRH2.S_su_in = (0.0, 'gCOD/L')
        self.concentrationsRH2.S_aa_in = (0.0, 'gCOD/L')
        self.concentrationsRH2.S_fa_in = (0.0, 'gCOD/L')
        self.concentrationsRH2.S_ac_in = (0.0, 'gCOD/L')
        self.concentrationsRH2.X_c_in = (2.0, 'gCOD/L')
        self.concentrationsRH2.X_ch_in = (0.0, 'gCOD/L')
        self.concentrationsRH2.X_pr_in = (0.0, 'gCOD/L')
        self.concentrationsRH2.X_li_in = (0.0, 'gCOD/L')
        self.concentrationsRH2.X_suaa_in = (0.0, 'g/L')
        self.concentrationsRH2.X_fa_in = (0.0, 'g/L')
        
        # Initial values of state variables 
        self.concentrationsRH2.S_su_0 = (0.012, 'gCOD/L')
        self.concentrationsRH2.S_aa_0 = (0.005, 'gCOD/L')
        self.concentrationsRH2.S_fa_0 = (0.099, 'gCOD/L')
        self.concentrationsRH2.S_ac_0 = (0.20, 'gCOD/L')
        self.concentrationsRH2.X_c_0 = (30.0, 'gCOD/L')
        self.concentrationsRH2.X_ch_0 = (0.028, 'gCOD/L')
        self.concentrationsRH2.X_pr_0 = (0.10, 'gCOD/L')
        self.concentrationsRH2.X_li_0 = (0.03, 'gCOD/L')
        self.concentrationsRH2.X_suaa_0 = (0.42, 'g/L')
        self.concentrationsRH2.X_fa_0 = (0.24, 'g/L')
        
        ############# CH4 Bioreactor ###############
        #Stoichiometric parameter values
        self.parametersRCH4.Y_ac = 0.5 #-
        
        #Biochemical parameter values
        self.parametersRCH4.k_m_ac = (8.0, '1/day')
        self.parametersRCH4.K_S_ac = (0.15, 'g/L') 
    
        # Physiochemical parameter values
        self.parametersRCH4.Y_ch4_ac = 1.0 #-
        
        # Physical parameter values
        self.parametersRCH4.V_liq_RCH4_del_V_liq_RH2 = (50.0, '-') #L/L

        # Input concentrations 
        self.concentrationsRCH4.X_ac_in = (0.0, 'g/L')
        
        # Initial values of state variables 
        self.concentrationsRCH4.S_ac_0 = (0.0, 'gCOD/L')
        self.concentrationsRCH4.X_ac_0 = (2.0, 'g/L')
        
        ############# Solver settings ###############
        self.solverSettings.tFinal = (50.0, 'day')
        self.solverSettings.tPrint = (0.1, 'day')
        self.solverSettings.absTol = (1e-9, 'day')
        self.solverSettings.relTol = (1e-7, 'day')
        
    def exampleADM1(self):
        ############# H2 Bioreactor ###############
        #Stoichiometric parameter values
        self.parametersRH2.f_ch_xc = 0.2 #-
        self.parametersRH2.f_pr_xc = 0.2 #-
        self.parametersRH2.f_li_xc = 0.3 #-
        
        self.parametersRH2.f_su_li = 0.05 #-
        self.parametersRH2.f_fa_li = 0.95 #-
        
        self.parametersRH2.f_ac_su = 0.41 #-
        
        self.parametersRH2.f_ac_aa = 0.4 #-
        
        self.parametersRH2.Y_suaa = 0.1 #-
        self.parametersRH2.Y_fa = 0.06 #-
        
        #Biochemical parameter values
        self.parametersRH2.k_dis = (0.5, '1/day')
        
        self.parametersRH2.k_hyd_ch = (10.0, '1/day')
        self.parametersRH2.k_hyd_pr = (10.0, '1/day')
        self.parametersRH2.k_hyd_li = (10.0, '1/day')
        
        self.parametersRH2.k_m_suaa = (30.0, '1/day')
        self.parametersRH2.K_S_suaa = (0.5, 'g/L')
        
        self.parametersRH2.k_m_fa = (6.0, '1/day')
        self.parametersRH2.K_S_fa = (0.4, 'g/L')
    
        # Physiochemical parameter values
        self.parametersRH2.Y_h2_su = 1.0 #-
        self.parametersRH2.Y_h2_aa = 1.0 #-
        self.parametersRH2.Y_h2_fa = 1.0 #-
        
        # Volumetric flow rate values
        self.parametersRH2.D_liq_arr[0] = (10.0, 0.0) #(day, 1/day)
        self.parametersRH2.D_liq_arr[1] = (10.0, 0.1) #(day, 1/day)
        self.parametersRH2.D_liq_arr[2] = (10.0, 0.05) #(day, 1/day)
        self.parametersRH2.D_liq_arr[3] = (10.0, 0.15) #(day, 1/day)
        
        # Input concentrations 
        self.concentrationsRH2.S_su_in = (0.01, 'gCOD/L')
        self.concentrationsRH2.S_aa_in = (0.001, 'gCOD/L')
        self.concentrationsRH2.S_fa_in = (0.001, 'gCOD/L')
        self.concentrationsRH2.S_ac_in = (0.001, 'gCOD/L')
        self.concentrationsRH2.X_c_in = (2.0, 'gCOD/L')
        self.concentrationsRH2.X_ch_in = (5.0, 'gCOD/L')
        self.concentrationsRH2.X_pr_in = (20.0, 'gCOD/L')
        self.concentrationsRH2.X_li_in = (5.0, 'gCOD/L')
        self.concentrationsRH2.X_suaa_in = (0.0, 'g/L')
        self.concentrationsRH2.X_fa_in = (0.01, 'g/L')
        
        # Initial values of state variables 
        self.concentrationsRH2.S_su_0 = (0.012, 'gCOD/L')
        self.concentrationsRH2.S_aa_0 = (0.005, 'gCOD/L')
        self.concentrationsRH2.S_fa_0 = (0.099, 'gCOD/L')
        self.concentrationsRH2.S_ac_0 = (0.20, 'gCOD/L')
        self.concentrationsRH2.X_c_0 = (0.31, 'gCOD/L')
        self.concentrationsRH2.X_ch_0 = (0.028, 'gCOD/L')
        self.concentrationsRH2.X_pr_0 = (0.10, 'gCOD/L')
        self.concentrationsRH2.X_li_0 = (0.03, 'gCOD/L')
        self.concentrationsRH2.X_suaa_0 = (0.42, 'g/L')
        self.concentrationsRH2.X_fa_0 = (0.24, 'g/L')
        
        ############# CH4 Bioreactor ###############
        #Stoichiometric parameter values
        self.parametersRCH4.Y_ac = 0.05 #-
        
        #Biochemical parameter values
        self.parametersRCH4.k_m_ac = (8.0, '1/day')
        self.parametersRCH4.K_S_ac = (0.15, 'g/L') 
    
        # Physiochemical parameter values
        self.parametersRCH4.Y_ch4_ac = 1.0 #-
        
        # Physical parameter values
        self.parametersRCH4.V_liq_RCH4_del_V_liq_RH2 = (50.0, '-') #L/L

        # Input concentrations 
        self.concentrationsRCH4.X_ac_in = (0.0, 'g/L')
        
        # Initial values of state variables 
        self.concentrationsRCH4.S_ac_0 = (0.0, 'gCOD/L')
        self.concentrationsRCH4.X_ac_0 = (0.76, 'g/L')
        
        ############# Solver settings ###############
        self.solverSettings.tFinal = (50.0, 'day')
        self.solverSettings.tPrint = (0.1, 'day')
        self.solverSettings.absTol = (1e-12, 'day')
        self.solverSettings.relTol = (1e-10, 'day')
                    
    def computeAsync(self):        
        # Simulate RH2 and RCH4 Bioreactors
        bioreactor = DM.ADM1H2CH4Bioreactors(self, 
                self.parametersRH2, self.concentrationsRH2,
                self.parametersRCH4, self.concentrationsRCH4)
        
        bioreactor.prepareSimulation(self.solverSettings)
        bioreactor.run(self.solverSettings)
        
        # Show results
        self.storage = bioreactor.resultStorage.simulationName
        