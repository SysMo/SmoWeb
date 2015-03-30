===================
Liquefaction cycles
===================

-------------------
Linde-Hampson cycle
-------------------

.. figure:: /static/ThermoFluids/img/ModuleImages/LindeHampson.svg
   :width: 500px
   :align: center
   
   Basic Linde-Hampson cycle
   
This is the simplest liquefaction cycle, used originally by Linde for air liquefaction. The 
cycle consists of the following steps:

* compression: the gas is compressed to a rather high pressure (200-300 bar). The compressor
  used is typically a multistage one with inter-cooling between the stages to approximate
  iso-thermal compression
* cooling: the fluid is cooled down to temperatures close to the liquefaction temperatures using
  a recurperator
* expansion: the fluid is expanded isenthalpically through a throttle valve; two-phase mixture
  forms and the liquid is separated from the vapor by allowing it to settle at the bottom of a
  reservoir
* gas return: the vapor fraction is returned to the compressor, passing through the recurperator,
  where it is warmed up and at the same time cools down the incoming flow from the compressor.

The Linde cycle has the advantage of simplicity, but it has 3 main problems:

* requires a compresssor for very high pressures
* very low yield: the liquid generated is only a small percent of the flow
* initial cool-down: the cycle cannot operate (at least not efficiently)
  until the cold side is already cold.  
   
------------
Claude cycle
------------

.. figure:: /static/ThermoFluids/img/ModuleImages/ClaudeCycle.svg
   :width: 500px
   :align: center
   
   Claude cycle

Calude cycle is built on top of the Linde-Hampson cycle, by adding an expander and two additional 
recurperators to the circuit [RefrigerationUSPAS]_. The expander extracts additional enthalpy from the fluid,
thus reducing the temperature and increasing the liquid yield. The downside is the increased complexity
of the circuit and especially the design of a low-temperature expander.

The Claude cycle has two variations:

* Kapitza cycle, which uses low pressures and a cryogenic expander, eliminating the last recurperator
* Heylandt cycle, which uses high pressures and a room-temperature expander, eliminating the first recurperator

Two examples of Kapitza cycles for Nitrogen with different pressure levels are implemented as examples, the data taken from:

* `Choudhury, B. K., Process Design of Turboexpander-based Nitrogen Liquefier <http://ethesis.nitrkl.ac.in/1466/1/PROCESS_DESIGN.pdf>`_, p. 27
* `Cryogenic cycles <http://direns.mines-paristech.fr/Sites/Thopt/en/co/cryogenie.html>`_, Claude cycle

----------
References
----------

.. [RefrigerationUSPAS] http://uspas.fnal.gov/materials/10MIT/Lecture_2.1.pdf

