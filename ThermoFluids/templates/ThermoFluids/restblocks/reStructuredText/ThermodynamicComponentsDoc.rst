========================
Thermodynamic components
========================

These components are used to build-up thermodynamic cycles (used in heat pumps, 
heat engines, liquefiers etc.)

----------
Compressor
----------

There are two models of compressor: isothermal and isentropic. They represent the two
extremes in terms of heat exchange with the environment. 

Isenttropic compressor compresses the fluid adiabatically (without exchanging heat with
the environmet). This model approximates a very quick compression model, where there is
not enough time for significat heat exchange with the environment. The outlet state of an
ideal isentropic heat exchanger has the same entropy as the inlet state. In reality, due
to friction and other irreversible processes, the entropy increases, and the real work is
higher than the ideal work, given by:

.. math::
   
   w_{id} = h\left(p_2, s_1\right) - h\left(p_1, s_1\right)
   
The isentropic efficiency of the compressor :math:`\eta` is a parameter of the compressor, 
such that:
   
.. math::
   
   w_{r} = w_{id} / \eta

where :math:`w_{r}` is the real specific work. A second parameter :math:`f_Q` defines the fraction
of the work, which is dissipated as heat in the environment:

.. math::
   
   q_{out} = w_{r} \cdot f_Q
   
Finally the real outlet state of the compressor can be computed by outlet pressure and specific enthalpy,
where the specific enthalpy is determined by energy balance:

.. math::
   
   h_{out} = h_{in} + w_{r} - q_{out}
 

Isothermal compressor compresses
the fluid (gas or liquid) at constant (ambient) temperature. It is the most efficient way
of compressing fluid (minimal work), however is not practically achievable. The compression
process has to be very slow in order for the temperature to constantly equilibrate with the
environment. To approach isothermal compression in reality a multiple stage compressor with
intercoolers can be used.

The heat flow to the environment is linked to the entropy change:

.. math::
   
   q_{out} = T * \left( s_{out} - s_{in} \right)
   
The work then is given by:

.. math::
   w_{r} = h_{out} - h_{in} + q_{out}

-------
Turbine
-------

The ideal turbine is also isentropic. A real turbine produces less work:

.. math::
   
   w_{r} = \eta\cdot w_{id}

The change of enthalpy is:

.. math::

   h_{out} = h_{in} + w_{r} - q_{out}
   
-------------------------------
Throttle (Joule-Thompson) valve
-------------------------------

Expansion through an orifice or capilary tube is isenthalpic (adiabatic and no work is produced).
Therefore

.. math::
   
   h_{out} = h_{in} 

However the temperature could decrease (near the two-phase region) or sometimes 
increase (at high pressures and temperatures).

----------------------
Evaporator / Condenser
----------------------

Pressure drop is neglected. No work is performed, so the change of enthalpy is equal to the heat
input to the fluid.

-------------------------
Two-stream heat exchanger
-------------------------

This is a general abstraction of a few different heat exchanger design concepts. It could be counter-flow,
parallel flow and cross-flow heat exchangers. The heat capacity flows are defined as:

.. math::
   
   {\dot Q}_1 = {\dot m}_1 \left( h(T_{2}^{in}, p_1) - h_{1}^{in} \right)
   
   {\dot Q}_2 = {\dot m}_2 \left( h(T_{1}^{in}, p_2) - h_{2}^{in} \right)
   
The maximal heat flow rate is the minimum of the two:

.. math::

   {\dot Q}_{max} = \min \left( {\dot Q}_1, {\dot Q}_2 \right)
   
Then the real heat flow rate is:

.. math::

   {\dot Q} = \varepsilon \cdot {\dot Q}_{max}
 
where :math:`\varepsilon` is the efficiency of the heat exchanger. 