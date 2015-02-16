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

For a pure fluid (fluid consisting of a single chemical species) two variables are necessary to 
completely describe its thermodynamic state. In theory, these could be any two from the following
list:

* pressure
* temperature
* density
* specific enthalpy
* specific entropy

In reality, there are good choices and bad choices of state variables. A choice could be also
good or bad depending on the particular state of the fluid. For an incompressible fluid, for
example, choosing the density as a state variable is apparently not suitable. Pressure and
temperature are always a good choice, except when properties are calculated in the two-phase region
(boiling/condensation). Temperature and density are always a good choice for compressible fluids.
Temperature and enthalpy are an unsuitable combination as they are strongly correlated, while pressure
and enthalpy are a very good combination. How suitable the selected combination of state variables is
depends also on the particular equations of state used. 

Two-phase region
----------------

If a liquid is heated beyond its boiling point at a pressure below its critical pressure, the fluid
starts evaporating. During evaporation the temperature and pressure are linked to each other, and 
if, for example, the pressure is kept constant, so remains the temperature. This part of the fluid state
diagram is called the two-phase region, because a partially evaporated fluid contains a liquid phase and a 
vapor phase. The mass fraction of the vapor phase is called vapor quality *q*. Thus :math:`q = 0` indicates
an all-liquid (saturated liquid) state, and :math:`q = 1` indicates a saturaded vapor state. The property of the
overall fluid in the two-phase region depends on the property of both phases and the *q*, e.g.

.. math::
   h = q \cdot h_v + (1 - q) \cdot h_l
   
   v = q \cdot v_v + (1 - q) \cdot v_l
   
where subscript *v* indicates vapor properties and subscript *l* - liquid ones.

In order to obtain the boiling temperature at a given pressure, the user enters the pressure and an arbitrary
value in the range 0-1 for *q*.

Equations of state
------------------


----------------
CoolProp package
----------------

All the fluid properties on this page are calculated using the open-source property 
package `CoolProp <http://www.coolprop.org/>`_. CoolProp is an open-source, 
cross-platform, free property database based on C++ that includes pure fluids, 
pseudo-pure fluids, and humid air properties. A complete list of all the materials
implemented in CoolProp can be found `here <http://www.coolprop.org/FluidInformation.html>`_

**Caution**: When using pseudo-pure fluids (like Air), there is a chance you may obtain funny values
for properties under ceratain conditions (e.g. at a low temperature). Thus, better use pure fluids 
(e.g. Nitrogen) whenever possible.

--------------
State diagrams
--------------

P-H diagram
-----------

Isentrops
~~~~~~~~~

1. Start from a seed poing :math:`f_0`
2. Compute the fluid state based on *p* and *h* variables
3. Find the direction of the isoline at point :math:`f_0`

.. math::
   \frac{\mathrm{d}h}{\mathrm{d}p}=\left(\frac{\partial h}{\partial p}\right)_{s}

4. Select a step :math:`\Delta p`
5. Find the :math:`\Delta h`:

.. math::

   \Delta h=v\Delta p+T\Delta s=v\Delta p
   
   
6. Find the changes  :math:`\Delta T` and :math:`\Delta\rho`:

.. math::
   \Delta\rho  =  \left(\frac{\partial\rho}{\partial h}\right)_{p}\Delta h+\left(\frac{\partial\rho}{\partial p}\right)_h\Delta p = 
   \left(\frac{\partial\rho}{\partial h}\right)_{p}v\Delta p+\left(\frac{\partial\rho}{\partial p}\right)_h\Delta p
   
   \Delta T = \left(\frac{\partial T}{\partial h}\right)_{p}\Delta h+\left(\frac{\partial T}{\partial p}\right)_h\Delta p =
   \frac{v\Delta p}{\left(\frac{\partial h}{\partial T}\right)_{p}}+\frac{\Delta p}{\left(\frac{\partial p}{\partial T}\right)_{h}}
 
   
7. Compute the fluid state at :math:`f_1` by :math:`T_0 + \Delta T` and :math:`\rho_0 + \Delta\rho`
8. Go back to 3. using :math:`f_1`

Isotherms
~~~~~~~~~

Steps 1 to 4 are as above

5. Find the :math:`\Delta h`:

.. math::
   \Delta h=\left(\frac{\partial h}{\partial p}\right)_{T}\Delta p
   
   \Delta h=v\Delta p+T\Delta s
   
   \left(\frac{\partial h}{\partial p}\right)_{T}=v\left(\frac{\partial p}{\partial p}\right)_{T}+T\left(\frac{\partial s}{\partial p}\right)_{T}
   =v+T\left(\frac{\partial s}{\partial p}\right)_{T}
   
   \Delta h=\left(v+T\left(\frac{\partial s}{\partial p}\right)_{T}\right)\Delta p
  
6. Find the change :math:`\Delta\rho`:

.. math::
   \Delta\rho=\left(\frac{\partial\rho}{\partial h}\right)_{p}\Delta h+\left(\frac{\partial\rho}{\partial p}\right)_{h}\Delta p
   =\left(\left(\frac{\partial\rho}{\partial h}\right)_{p}\left(v+T\left(\frac{\partial s}{\partial p}\right)_{T}\right)+\left(\frac{\partial\rho}{\partial p}\right)_{h}\right)\Delta p
 
 
   
   
 