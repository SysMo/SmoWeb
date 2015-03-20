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

A chemostat (from "Chemical environment is static") is a bioreactor to which fresh medium with nutrient (substrate) is continuously added, 
while culture liquid is continuously removed to keep the culture volume constant. By changing the rate 
at which medium is added to the bioreactor the growth rate of the culture (microorganism) can be easily controlled [Wiki-Chemostat]_.

Mathematical model
------------------
The mathematical model of a simple chemostat is [Chemostat95]_:

.. math::   
   S' = (S_{in} - S)D - \frac{1}{\gamma}\mu(S)X
   
   X' = -DX + \mu(S)X
   

where:
   
   :math:`S(t)` - the substrate concentration [mass/volume]
   
   :math:`X(t)` - the microorganisms concentration [mass/volume]
   
   :math:`S_{in}` - the input substrate concentration [mass/volume]
   
   :math:`D` - the dilution (or washout) rate [1/time]
   
   :math:`\gamma` - the yield coefficient of microorganisms (:math:`\gamma \leq 1`) [-]
   
   :math:`\mu(S) = \frac{m.S}{K+S}` - the specific growth rate (Monod type) [mass/volume-time]
   
   :math:`m` - the maximum specific growth rate of the microorganisms [1/time]
   
   :math:`K` - the half saturation constant [mass/volume]
   
and
   
   :math:`S'=\frac{dS(t)}{dt}` - the rate of change of the substrate concentration [mass/volume-time]

   :math:`X'=\frac{dX(t)}{dt}` - the rate of change of the microorganisms concentration [mass/volume-time]



In simple words, the above ordinary differential equations say:

.. math::

   \mbox{the rate of change of the substrate = input - washout - consumption}
   
   \mbox{the rate of change of the microorganisms = - washout + growth}


References
----------

.. [Wiki-Chemostat] http://en.wikipedia.org/wiki/Chemostat
.. [Chemostat95] Smith, H. and Waltman, P. The Theory of the Chemostat: Dynamics of Microbial Competition. Cambridge University Press, 1995
