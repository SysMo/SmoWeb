========================
Thermodynamic components
========================

These components are used to build thermodynamic cycles (used in heat pumps, 
heat engines, liquefiers, etc.)

----------
Compressor
----------

There are two compressor models: isothermal and isentropic. They represent the two
extremes in terms of heat exchange with the environment. 

An isentropic compressor compresses the fluid adiabatically (without exchanging heat with
the environment). This model approximates a very quick compression model, where there is
not enough time for significant heat exchange with the environment. The outlet state of an
ideal isentropic heat exchanger has the same entropy as the inlet state. In reality, due
to friction and other irreversible processes, the entropy increases and the real work is
higher than the ideal work, which is given by:

.. math::
   
   w_{id} = h\left(p_2, s_1\right) - h\left(p_1, s_1\right)
   
The isentropic efficiency of the compressor :math:`\eta` is a parameter of the compressor such that:
   
.. math::
   
   w_{r} = w_{id} / \eta

where :math:`w_{r}` is the real specific work. A second parameter :math:`f_Q` defines the fraction
of the work that is dissipated as heat in the environment:

.. math::
   
   q_{out} = w_{r} \cdot f_Q
   
Finally, the real outlet state of the compressor can be computed by outlet pressure and specific enthalpy,
where the specific enthalpy is determined by the energy balance:

.. math::
   
   h_{out} = h_{in} + w_{r} - q_{out}
 

An isothermal compressor compresses
the fluid (gas or liquid) at constant (ambient) temperature. It is the most efficient way
of compressing fluid (minimal work), although it is not feasible. The compression
process has to be very slow in order for the temperature to constantly equilibrate with the
environment. To approach isothermal compression in practice, a multiple-stage compressor with
intercoolers can be used.

The heat flow to the environment is linked to the entropy change:

.. math::
   
   q_{out} = T * \left( s_{out} - s_{in} \right)
   
Then the work is given by:

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

However, the temperature could decrease (near the two-phase region) or sometimes 
increase (at high pressures and temperatures).

----------------------
Evaporator / Condenser
----------------------

Pressure drop is neglected. No work is done, so the change of enthalpy is equal to the heat
input to the fluid.

-------------------------
Two-stream heat exchanger
-------------------------

This is a general abstraction of a few different heat exchanger design concepts. The heat exchangers could be counter-flow,
parallel-flow and cross-flow. The heat capacity flows are defined as:

.. math::
   
   {\dot Q}_1 = {\dot m}_1 \left( h(T_{2}^{in}, p_1) - h_{1}^{in} \right)
   
   {\dot Q}_2 = {\dot m}_2 \left( h(T_{1}^{in}, p_2) - h_{2}^{in} \right)
   
The maximal possible heat flow rate, which can be achieved in an infinetely long countercurrent heat exchanger, is the lesser of the two:

.. math::

   {\dot Q}_{m} = \min \left( {\dot Q}_1, {\dot Q}_2 \right)
   
Then the real heat flow rate is:

.. math::

   {\dot Q} = \varepsilon \cdot {\dot Q}_{m}
 
where :math:`\varepsilon` is the *effectiveness* of the heat exchanger. In the :math:`NTU-\varepsilon` method [Wiki-NTU]_, the effectiveness
is determined as a function of the *number of transfer units* and the *heat capacity ratio*:

.. math::
    \varepsilon = f\left( NTU, C_r \right)
    
    NTU = \frac{U \cdot A}{\dot{C}_{min}}
    
    C_r = \frac{\min\left(\dot{Q}_{1},\dot{Q}_{2}\right)}{\max\left(\dot{Q}_{1},\dot{Q}_{2}\right)}
    
where :math:`\dot{C}_{min} = {\dot Q}_{m} / (T_1^{in} - T_2^{in})`, :math:`U` is the overall heat transfer coefficient, and :math:`A` is the heat exhcange area

The effectiveness formula depends on the flow configuration, as shown in the table below:

.. class:: nice-table

+----------------------------+-------------------------------------------------------------------------------------------+
| Flow configuration         | Effectiveness correlation                                                                 |
+============================+===========================================================================================+
| parallel flow              | :math:`\varepsilon \ = \frac {1 - \exp[-NTU(1 + C_{r})]}{1 + C_{r}}`                      |
+----------------------------+-------------------------------------------------------------------------------------------+
| counter-current flow       | :math:`\varepsilon \ = \frac {1 - \exp[-NTU(1 - C_{r})]}{1 - C_{r}\exp[-NTU(1 - C_{r})]}` |
+----------------------------+-------------------------------------------------------------------------------------------+
| evaporation / condensation | :math:`\varepsilon \ = 1 - \exp[-NTU]`                                                    |
+----------------------------+-------------------------------------------------------------------------------------------+


----------
References
----------

.. [Wiki-NTU] Wikipedia, NTU method, http://en.wikipedia.org/wiki/NTU_method