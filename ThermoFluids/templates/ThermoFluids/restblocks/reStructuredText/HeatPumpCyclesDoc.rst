================
Heat pump cycles
================

Heat pumps utilize work to move heat from colder to warmer places. This is used in cooling devices (refrigerators, freezers) and in air conditioners
for either cooling or more effective heating. The same cycle design can be used either for cooling (if it realeses heat to the environment) or heating
(if it absorbs heat from the environment). The measure of the efficiency of the cycle is its *COP* (coefficient of performance) which gives the amount of
useful heating or cooling capacity per unit input work. That is:

.. math::

   COP_{cooling} = \frac {Q_C}{W}
   
   COP_{heating} = \frac {Q_H}{W}
   
Typically (neglecting thermal losses) :math:`COP_{heating} = COP_{cooling} + 1 `, because :math:`Q_H = Q_C + W`

-----------------------
Vapor compression cycle
-----------------------

.. figure:: /static/ThermoFluids/img/ModuleImages/VaporCompressionCycle.svg
   :width: 500px
   :align: center
   
   Basic vapor compression cycle
   
The simplest vapor compression cycle consists of four steps:

#. The refrigerant vapors are compressed nearly adiabatically
#. The high pressure hot vapors pass through a condensor where they give off heat to the environment 
   and cool and liquefy at constant pressure (in case of transcritical cycle :math:'p_H > p_{crit}',
   no liquefaction takes place, but only cooling.
#. The subcooled high pressure liquid is allowed to expand through a Joule-Thompson (throttle)
   valve at a constant enthalpy (no work is done, no heat exchange with the environment). This causes 
   part of the liquid to vaporize, and the temperature to drop significantly, resulting in two-phase
   mixture. The colder the temperature of the fluid before the valve, the more the fraction of the liquid
#. The cold two-phase mixture evaporates at constant pressure at the evaporator absorbing heat from the
   environment
   
-----------------------------------------
Vapor compression cycle with recuperator
-----------------------------------------

.. figure:: /static/ThermoFluids/img/ModuleImages/VaporCompressionCycle.svg
   :width: 500px
   :align: center
   
   Vapor compression cycle with recuperator

In this variation of the vapor compression cycle, a recuperator (counterflow heat exchanger) is placed
between:

* the otlet of the evaporator and the inlet of the compressor, on one hand, 
* the outlet of the condenser and the inlet of the throttle valve, on the other hand. 

The cold vapors coming from the evaporator, which still have some
cooling capacity, absorb heat from the still warm liquid leaving the condensor. The subcooling of the liquid
before the throttle valve, shifts the two-phase mixture entering the evaporator to the liquid side, and thus
provides extra cooling capacity. The temperature at the outlet of the compressor also increases, resulting
in more heat rejected at the condensor.
 
