===============
Flow resistance
===============

----------
Parameters
----------

+-----------------+------------------------+
| Symbol          | Parameter name         |
+=================+========================+
| :math:`d_i`     | internal pipe diameter |
+-----------------+------------------------+
| :math:`d_e`     | external pipe diameter |
+-----------------+------------------------+
| :math:`L`       | pipe length            |
+-----------------+------------------------+
| :math:`p_i`     | inlet pressure         |
+-----------------+------------------------+
| :math:`T_i`     | inlet temperature      |
+-----------------+------------------------+
| :math:`\dot{m}` | inlet mass flow rate   |
+-----------------+------------------------+

-------------------
Geometry properties
-------------------
The flow area is

.. math ::
   A_f = \frac{\pi d_i^2}{4}
   
The fluid volume is:

..  math::
   V = A_f L

The internal and external surface areas are calculated as:

..  math::

   A_i = \pi d_i L

   A_e = \pi d_e L
   
The mass of the pipe is:

..  math::

   m_p =  \rho_p \frac{\pi \left( d_e^2 - d_i^2 \right)}{4}L
   
where :math:`\rho_p` is the density of the pipe material (steel, aluminium etc.) 

-------------
Pressure drop
-------------
In general the pressure drop in pipes and components depends on the upstream fluid density :math:`\rho` and flow velocity 

.. math::
   v = \frac{\dot{m}}{\rho A_{f}}

and can be calculated from the formula:

..  math::   
   \Delta p=c_{d}\frac{\rho v^{2}}{2},

where :math:`c_{d}` is the flow drag coefficient. For pipes the drag coefficient depends on the pipe geometry and the *Darcy friction factor*:

.. math::   
   c_{d}=\zeta\frac{L}{d_i}
   
where :math:`\zeta` is the friction factor, :math:`L` is the length of the pipe and :math:`d` is the internal diameter of the pipe.

..  math::
   \zeta =  8\left[\left(\frac{8}{Re}\right)^{12}+\frac{1}{\left(\Theta_{1}+\Theta_{2}\right)^{1.5}}\right]^{\frac{1}{12}}
   
   \Theta_{1}  =  \left[2.457\cdot\ln\left(\left(\frac{7}{Re}\right)^{0.9}+0.27\frac{\varepsilon}{d}\right)\right]^{16}
   
   \Theta_{2}  =  \left(\frac{37530}{Re}\right)^{16}
 