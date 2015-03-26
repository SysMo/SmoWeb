==================
Heat engine cycles
==================

Heat engines produce useful work by allowing heat to move from a hot reservoir to a cold reservoir.
Examples of heat engines are the steam and gas turbines in power plants and internal combustion engines
powering vehicles. The cold reservoir is usually the environment, so the efficiency of the cycle is 
measured as the fraction of the heat coming from the hot reservoir converted to work:

.. math::
   
   \eta = \frac{W}{Q_H}
   
If the hot and cold reservoir have a well defined temperature, then the maximum efficiency that
can be achieved is given by Carnot's efficiency:

.. math::
   \eta_c = 1 - \frac{T_C}{T_H}
   
Provided that we operate between two such fixed temperature reservoirs, a measure of how good the
cycle design is, is the *second law* efficiency:

.. math::
   \eta_{2nd} = \frac {\eta} {\eta_c}
   
-------------
Rankine cycle
-------------

.. figure:: /static/ThermoFluids/img/ModuleImages/RankineCycle.svg
   :width: 500px
   :align: center
   
   Rankine cycle

Rankine cycle is used to produce power in virtually all coal power plants and other plants using
steam turbines to power generators. It consists of four steps:

#. The cold liquid water is pumped to high pressure using a liquid pump. Because liquids are nearly
   incompressible the work required for the pumping is rather small
#. The water enters a boiler where it is heated (by burning coal etc.). The water evaporates and the
   steam is typically superheated (both processes at constant pressure) so that the steam is well away
   from the two-phase region (dry steam)
#. The hot, high-pressure steam is expanded through a turbine, isentropically (in an ideal cycle),
   and part of the steam enthalpy is converted to work. At the outlet, wet steam (two-phase
   mixture, mostly steam) at low pressure exits the turbine
#. The wet steam enters the condenser, gives off heat to the environment and is reliquefied before
   being pumped again.

--------------------------
Regenerative Rankine cycle
--------------------------

.. figure:: /static/ThermoFluids/img/ModuleImages/RankineCycle_Recuperator.png
   :width: 500px
   :align: center
   
   Regenerative Rankine cycle

In this variation of the Rankine cycle, a counterflow heat exchanger (recuperator) is placed between:
 
* the pump and the boiler on one hand
* the turbine and the condenser on the other hand
 
The steam exiting the turbine is still rather hot. Some of its enthalpy can be used to pre-heat the water
entering the boiler, before it is wasted by rejecting it to the surroundings. This reduces the amount of
heat necessary to produce the steam, and therefore increases the efficiency of the cycle.
  