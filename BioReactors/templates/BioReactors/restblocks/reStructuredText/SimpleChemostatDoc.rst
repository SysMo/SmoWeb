.. sectnum::
   :suffix: .

================
Simple Chemostat
================

.. figure:: /static/BioReactors/img/ModuleImages/SimpleChemostat.png
   :width: 150px
   :align: center
   
   Stirred bioreactor operated as a chemostat, with a continuous inflow (the feed) and outflow (the effluent). 
   The rate of medium flow is controlled to keep the culture volume constant.


Chemostat
---------

A chemostat (from Chemical environment is static) is a bioreactor to which fresh medium is continuously added, 
while culture liquid is continuously removed to keep the culture volume constant. By changing the rate 
with which medium is added to the bioreactor the growth rate of the microorganism can be easily controlled [Wiki-Chemostat]_.

Mathematical model
------------------
The mathematical model of simple chemostat is [Chemostat:95]_:

.. math::   
   S' = (S_{in} - S)D - \frac{1}{\gamma}\mu(S)X
   
   X' = -DX + \mu(S)X
   

where:

:math:`S(t)` - concentration of nutrient (substrate) [mass/volume]

:math:`X(t)` - concentration of culture (microorganisms) [mass/volume]

:math:`S_{in}` - concentration of the input nutrient (substrate) [mass/volume]

:math:`D` - dilution (or washout) flow rate [1/time]

:math:`\gamma` - yield coefficient of microorganisms (:math:`\gamma <= 1`) [-]

:math:`\mu(S) = \frac{m.S}{K+S}` - specific growth rate (Monod type)

:math:`m` - maximal growth rate [1/time]

:math:`K` - half saturation constant [mass/volume]



References
----------
 
.. [Wiki-Chemostat] http://en.wikipedia.org/wiki/Chemostat
.. [Chemostat:95] H. Smith and P. Waltman. The Theory of the Chemostat: Dynamics of Microbial Competition. Cambridge University Press, 1995
