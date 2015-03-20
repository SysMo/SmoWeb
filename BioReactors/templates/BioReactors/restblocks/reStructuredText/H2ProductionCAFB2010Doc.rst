.. sectnum::
   :suffix: .

============================================================================
Hydrogen production in a continuous anaerobic fermentation bioreactor (CAFB)
============================================================================

.. figure:: /static/BioReactors/img/H2ProductionCAFB2010/H2ProductionCAFB2010_SchematicView.png
   :width: 500px
   :align: center
   
   Schematic view of the continuous anaerobic fermentation bioreactor using in the source paper.

The source paper: [H2ProductionCAFB:2010]_

Introduction
------------
One of the great challenges of this century is to obtain new sources of renewable energy, 
capable of replacing fossil fuels. Biological processes have shown strong potentialities 
for sustainable H\ :sub:`2` production, while hydrogen is presently mainly produced from the 
reforming of fossil materials (90% of world production, 45 billion tons) with a high level 
of pollution generated [SustaninableEnergy:2003]_.

Hydrogen can be produced by microorganisms using two enzymes (i.e., hydrogenase and 
nitrogenase) active in their metabolic pathways. The involved processes of biohydrogen 
production can be classified into three main classes: biophotolysis, photodecomposition 
and acidogenic fermentation of carbohydrates (i.e., acidogenesis). The two first processes 
are photobiological (i.e., light is needed) while the acidogenesis step presents several 
advantages such as a production yield higher than those obtained with photobiological 
processes and the capacity of working all day long (i.e., even with nolight) [H2Production:2001]_.

Mathematical model
------------------
In the source paper authors used a general mass balance model of a continuous 
stirred tank reactor fed with carbohydrates. While molasses contain only carbohydrates like 
sucrose, fructose and glucose and because of the fast hydrolysis of sucrose, they considered 
that all the carbohydrates are represented by glucose. The mathematical model of glucose 
metabolism performed by a single microorganism producing acetate, propionate, butyrate, 
biomass, carbon inorganic (i.e., CO\ :sub:`2`, HCO\ :sup:`-`\ :sub:`3`, etc.) and hydrogen is:

.. math::   
   \frac{d}{dt}\left[\begin{array}{c}
   Glu\\
   Ace\\
   Pro\\
   Bu\\
   X\\
   CO_{2}\\
   H_{2}
   \end{array}\right]=Y\cdot r-D\left[\begin{array}{c}
   Glu\\
   Ace\\
   Pro\\
   Bu\\
   X\\
   CO_{2}\\
   H_{2}
   \end{array}\right]+D\left[\begin{array}{c}
   Glu_{in}\\
   0\\
   0\\
   0\\
   0\\
   0\\
   0
   \end{array}\right]-D\left[\begin{array}{c}
   0\\
   0\\
   0\\
   0\\
   0\\
   q_{CO_{2}}\\
   q_{H_{2}}
   \end{array}\right]
    
where the state variables Glu, Ace, Pro, Bu, X, CO\ :sub:`2` and H\ :sub:`2` represent,
respectively, the concentrations in [gL\ :sup:`-1`] of glucose, acetate, propionate, 
butyrate, biomass; carbon dioxide (in [mol L\ :sup:`-1`]) and dissolved hydrogen in the 
liquid phase (in [gL\ :sup:`-1`]). The vector :math:`r` describes the kinetics of the involved 
biological reactions (in  [g L\ :sup:`-1` h\ :sup:`-1`]), D is the dilution rate [h\ :sup:`-1`] 
and :math:`q_{CO_{2}}` and :math:`q_{H_{2}}` the gas flow rates of carbon dioxide 
(in [mol L\ :sup:`-1` h\ :sup:`-1`]) and hydrogen (in [g L\ :sup:`-1` h\ :sup:`-1`]). :math:`Y` 
represents the matrix of pseudo-stoichiometric coefficients, i.e. 

.. math:: 
   \begin{array}{cc}
   r=\left[\begin{array}{c}
   \frac{\rho_{max,1}\cdot Glu}{K_{Glu,1}+Glu}X\\
   \frac{\rho_{max,2}\cdot Glu}{K_{Glu,2}+Glu}X
   \end{array}\right] & \; Y=\left[\begin{array}{cc}
   -1 & -1\\
   0 & w_{22}\\
   0 & w_{32}\\
   w_{41} & w_{42}\\
   w_{51} & 0\\
   w_{61} & w_{62}\\
   w_{71} & 0
   \end{array}\right]\end{array}
   
where: 

   - :math:`w_{i,j}` are pseudo-stoichiometric coefficients 
   - :math:`\rho_{max,1}` is maximal growth rate [h\ :sup:`-1`] of hydrogen production
   - :math:`\rho_{max,2}` is maximal growth rate [h\ :sup:`-1`] of acid production
   - :math:`K_{Glu,1}` is half saturation constant [g L\ :sup:`-1`] of hydrogen production
   - :math:`K_{Glu,2}` is half saturation constant [g L\ :sup:`-1`] of acid production 

 
The kinetics of the involved biological reactions could be expressed in a 
Petersen matrix form:

.. figure:: /static/BioReactors/img/H2ProductionCAFB2010/H2ProductionCAFB2010_PetersonMatrix.png
   :width: 750px
   :align: center
   
   Pseudo-stoichimetric matrix of hydrogen production expressed in Petersen matrix form.
   

References
----------
.. [SustaninableEnergy:2003] Maddy J, Cherryman S, Hawkes FR, Hawkes DL, Dinsdale RM, Guwy AJ, et al. 
   HYDROGEN 2003 report number 1 ERDF part-funded project entitled: 
   “a sustainable energy supply for wales: towards the hydrogen economy”. 
   University of Glamorgan; 2003.
   
   
.. [H2ProductionCAFB:2010] Cesar-Arturo Aceves-Lara, Eric Latrille, Jean-Philippe Steyer, 
   Optimal control of hydrogen production in a continuous anaerobic fermentation bioreactor, 
   International Journal of Hydrogen Energy, Vol. 35(19), 2010, 10710-10718.
   
   
.. [H2Production:2001] Das D, Veziroglu TN. Hydrogen production by biological processes: a survey of literature. 
   Int J Hydrogen Energy 2001; 26:13e28.