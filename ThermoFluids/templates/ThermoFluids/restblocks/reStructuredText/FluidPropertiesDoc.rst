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

A special algorithm was developed for tracing isentrops, so that most calculations can be expressed in terms
of the fundamental variables of the equation of state: temperature and density.

1. Start from a seed poing :math:`f_0`
2. Compute the fluid state based on :math:`s` and :math:`T` variables
3. Find :math:`\left(\frac{\partial\rho}{\partial T}\right)_{s}`.
4. Select a step :math:`\Delta T` and find :math:`\Delta \rho` from

.. math::
   \frac{\mathrm{d}\rho}{\mathrm{d}T}=\left(\frac{\partial \rho}{\partial T}\right)_{s}

5. Compute the fluid state at :math:`f_1` by :math:`T_0 + \Delta T` and :math:`\rho_0 + \Delta\rho`
6. Go back to 3. using :math:`f_1`

We use Maxwell relations to find the derivative:

.. math::
   \left(\frac{\partial v}{\partial T}\right)_{s}=-\left(\frac{\partial s}{\partial p}\right)_{v}
   
Which can be expressed as:

.. math::
   :name: eq:pfx

   \left(\frac{\partial\rho}{\partial T}\right)_{s}=\rho^2\cdot\left(\frac{\partial s}{\partial p}\right)_{v}


Using the total derivative of :math:`s`:

.. math::
   \mathrm{d}s=\left(\frac{\partial s}{\partial v}\right)_{T}\cdot \mathrm{d}v+\left(\frac{\partial s}{\partial T}\right)_{v}\cdot \mathrm{d}T

And taking the partial derivative:

.. math::
   \left(\frac{\partial s}{\partial p}\right)_{v}=\left(\frac{\partial s}{\partial v}\right)_{T}\cdot\left(\frac{\partial v}{\partial p}\right)_{v}+\left(\frac{\partial s}{\partial T}\right)_{v}\cdot\left(\frac{\partial T}{\partial p}\right)_{v}

   \left(\frac{\partial s}{\partial p}\right)_{v}=\left(\frac{\partial s}{\partial T}\right)_{v}\cdot\left(\frac{\partial T}{\partial p}\right)_{v}


Finally:

.. math::
   \left(\frac{\partial \rho}{\partial T}\right)_{s}=\rho^2\left(\frac{\partial s}{\partial T}\right)_{v}\cdot\left(\frac{\partial T}{\partial p}\right)_{v}


In the single phase region the two partial derivatives on the right can be calculated directly. In the two-phase region, we can use: 

.. math::
   s=q\cdot s_{V}+(1-q)\cdot s_{L}

And therefore the total :math:`s` derivative can be expressed as:

.. math::
   \partial s=\left(\frac{\partial s}{\partial q}\right)_{T}\mathrm{d}q+\left(\frac{\partial s}{\partial T}\right)_{q}\mathrm{d}T

Taking the partial derivative:

.. math::
   \left(\frac{\partial s}{\partial T}\right)_{v}=\left(\frac{\partial s}{\partial q}\right)_{T}\cdot\left(\frac{\partial q}{\partial T}\right)_{v}+\left(\frac{\partial s}{\partial T}\right)_{q}\cdot\left(\frac{\partial T}{\partial T}\right)_{v}
   
   \left(\frac{\partial s}{\partial T}\right)_{v}=\left(\frac{\partial s}{\partial q}\right)_{T}\cdot\left(\frac{\partial q}{\partial T}\right)_{v}+\left(\frac{\partial s}{\partial T}\right)_{q}
 

The terms can be expressed as follows:

.. math::
   \left(\frac{\partial s}{\partial q}\right)_{T}=s_{V}-s_{L}
   
   \left(\frac{\partial q}{\partial T}\right)_{v}=-\frac{\left(\frac{\partial v}{\partial T}\right)_{q}}{\left(\frac{\partial v}{\partial q}\right)_{T}}

   \left(\frac{\partial s}{\partial T}\right)_{q}=q\cdot\left(\frac{\partial s}{\partial T}\right)_{SatV}+\left(1-q\right)\cdot\left(\frac{\partial s}{\partial T}\right)_{SatL}
   
   
The right-hand side of the second equation contains two terms, which can be expressed as follows:

.. math:: 
   \left(\frac{\partial v}{\partial T}\right)_{q}=q\cdot\left(\frac{\partial v}{\partial T}\right)_{SatV}+\left(1-q\right)\cdot\left(\frac{\partial v}{\partial T}\right)_{SatL}

   \left(\frac{\partial v}{\partial q}\right)_{T}=v_{V}-v_{L}

Therefore we have:

.. math:: 
   \left(\frac{\partial q}{\partial T}\right)_{v}=-\frac{q\cdot\left(\frac{\partial v}{\partial T}\right)_{SatV}+\left(1-q\right)\cdot\left(\frac{\partial v}{\partial T}\right)_{SatL}}{v_{v}-v_{L}}
 
   \left(\frac{\partial q}{\partial T}\right)_{v}=\frac{\frac{q}{\rho^{2}}\left(\frac{\partial\rho}{\partial T}\right)_{SatV}+\frac{1-q}{\rho^{2}}\left(\frac{\partial\rho}{\partial T}\right)_{SatL}}{\frac{1}{\rho_{v}}-\frac{1}{\rho_{L}}}   
 


   


Isochores
~~~~~~~~~

Determine the appropriate ranges for :math:`T` and :math:`\rho` and 
compute the fluid state based on those variables

Isotherms
~~~~~~~~~

Same as in the case of isochores