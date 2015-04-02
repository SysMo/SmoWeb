.. sectnum::
   :suffix: .

===============
Chemostat (DDE)
===============

.. figure:: /static/BioReactors/img/ModuleImages/SimpleChemostat.png
   :width: 150px
   :align: center
   
   Stirred bioreactor operated as a chemostat, with continuous inflow (the feed) and outflow (the effluent).


Delay differential equations (DDE)
----------------------------------
Delay differential equations (DDEs) are a type of differential equations in which the derivative 
of the unknown function at a certain time is given in terms of the values of the function at previous times.
The general form of the time-delay differential equation for :math:`x(t)` is

.. math::
   x'(t) = f(t, x(t), x_{t})

where :math:`x_t=\{x(\tau):\tau\leq t\}` represents the trajectory of the solution in the past [Wiki-DDE]_.


Mathematical model
------------------
One example of a mathematical model of a chemostat with delay differential equations (DDE) is:

:math:`s'_{1}(t)=D\left(s_{1}^{in}-s_{1}(t)\right)-k_{1}\mu_{1}\left(s_{1}(t)\right)x_{1}(t)`
   
:math:`x'_{1}(t)=\mu_{1}\left(s_{1}(t-\tau_{1})\right)x_{1}(t-\tau_{1})-\alpha Dx_{1}(t)`
   
:math:`s'_{2}(t)=D\left(s_{2}^{in}-s_{2}(t)\right)+k_{2}\mu_{1}\left(s_{1}(t)\right)x_{1}(t)-k_{3}\mu_{2}\left(s_{2}(t)\right)x_{2}(t)`
   
:math:`x'_{2}(t)=\mu_{2}\left(s_{2}(t-\tau_{2})\right)x_{2}(t-\tau_{2})-\alpha Dx_{2}(t)`
   
|

where:

|
   
:math:`s_{1}, s_{2}` - the substrate concentrations
   
:math:`x_{1}, x_{2}` - the bacteria concentrations

:math:`s_{1}^{in}, s_{2}^{in}` - the input substrate concentrations 
     
:math:`D` - the dilution (or washout) rate
   
:math:`k_{1}, k_{2}, k_{3}` - the yield coefficients
   
:math:`\alpha` - the proportion of bacteria that are affected by the dilution rate D
   
:math:`\tau_{1}, \tau_{2}` - the time delay in conversion of the corresponding substrate to viable biomass for the i-th bacterial population 
   
:math:`\mu_{1}(s_{1}) = \frac{m_{1}s_{1}}{k_{s1}+s_{1}}` - the specific growth rate of the bacteria-1
   
:math:`\mu_{2}(s_{2}) = \frac{m_{2}s_{2}}{k_{s2}+s_{2}+(s_{2}/k_{I})^{2}}` - the specific growth rate of the bacteria-2
   
:math:`m_{1}, m_{2}` - the maximum specific growth rates of the bacteria
   
:math:`k_{s1}, k_{s2}` - the half saturation constants
   
:math:`k_{I}` - constant
   
References
----------

.. [Wiki-DDE] http://en.wikipedia.org/wiki/Delay_differential_equation