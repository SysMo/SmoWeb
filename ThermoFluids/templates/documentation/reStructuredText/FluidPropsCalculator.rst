.. sectnum::
   :suffix: .

================
Fluid Properties
================

--------------------
Fluid property input
--------------------

Choice of state variables
-------------------------

A pure fluid (fluid consisting of a single chemical species) 2 variables are necessary to 
complety describe its thermodynamic state. In theory these could be any 2 of the following
list:

* pressure
* temperature
* density
* specific enthalpy
* specific entropy

In reality there are good choices and bad choices of state variables. A choice could be also
good or bad depending on the particular state of the fluid. For incompressible fluid, for
example, choosing the density as a state variable is apparently not suitable. Pressure and
temperature are always a good choice, except when properties are calculated in the 2-phase region
(boiling/condensation). Temperature and density are always a good choice for compressible fluids.
Temperature and enthalpy are unsuitable combination as they are strongly correlated, while pressure
and enthalpy are a very good combination. How suitable the selected combination of state variables is,
depends also on the particular equations of state used. 

Two-phase region
----------------

If a liquid is heated beyond its boiling point at a pressure below its critical pressure, the fluid
starts evaporating. During evaporation the temperature and pressure are linked to each other, and 
if e.g. the pressure is kept constant, so remains the temperature as well. This part of the fluid state
diagram is called 2-phase region, because a partially evaporated fluid contains a liquid phase and a 
vapor phase. The mass fraction of the vapor phase is called vapor quality *q*. Thus :math:`q = 0` indicates
all-liquid (saturated liquid) state, and :math:`q = 1` indicates saturaded vapor state. The property of the
overall fluid in the 2-phase region depends on the property of both phases and the *q*, e.g.

.. math::
   h = q \cdot h_v + (1 - q) \cdot h_l
   
   v = q \cdot v_v + (1 - q) \cdot v_l
   
where subscript *v* indicates vapor properties and subscript *l* - liquid.

In order to obtain the boiling temperature at a given pressure, the user enthers the pressure and arbitrary
value in the range 0-1 for *q*.

Equations of state
------------------


----------------
CoolProp pacakge
----------------

All the fluid properties on this page are calculated using the open-source property 
package `CoolProp <http://www.coolprop.org/>`_. CoolProp is an open-source, 
cross-platform, free property database based in C++ that includes pure fluids, 
pseudo-pure fluids, and humid air properties. A complete list of all the materials
implemented in CoolProp can be found `here <http://www.coolprop.org/FluidInformation.html>`_

**Caution**: When using pseudo-pure fluids (like Air), there is a chance you obtain funny values
for properties under ceratain conditions (e.g. at low temperature). So, better use pure fluids 
(e.g. Nitrogen) whenever possible.

