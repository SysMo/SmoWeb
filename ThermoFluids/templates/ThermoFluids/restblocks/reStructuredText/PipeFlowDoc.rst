.. sectnum::
   :suffix: .

=========
Pipe Flow
=========

.. figure:: /static/ThermoFluids/img/StraightPipe.svg
   :width: 500px
   :align: center
   
   Pipe parameters

----------
Parameters
----------

.. class:: nice-table

+---------------------+------------------------+------+
| Symbol              | Parameter name         | Unit |
+=====================+========================+======+
| :math:`d_i`         | internal pipe diameter | mm   |
+---------------------+------------------------+------+
| :math:`d_e`         | external pipe diameter | mm   |
+---------------------+------------------------+------+
| :math:`L`           | pipe length            | m    |
+---------------------+------------------------+------+
| :math:`\varepsilon` | pipe surface roughness | mm   |
+---------------------+------------------------+------+
| :math:`p_i`         | inlet pressure         | bar  |
+---------------------+------------------------+------+
| :math:`T_i`         | inlet temperature      | K    |
+---------------------+------------------------+------+
| :math:`\dot{m}`     | inlet mass flow rate   | kg/h |
+---------------------+------------------------+------+

-------------------
Geometry properties
-------------------
The flow area is:

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
   
where :math:`\rho_p` is the density of the pipe material (steel, aluminum etc.) 

---------------
Pressure losses
---------------
In general the pressure loss in pipes and components depends on the upstream fluid density :math:`\rho` and the flow velocity 

.. math::
   v = \frac{\dot{m}}{\rho A_{f}}

This pressure loss can be calculated from the formula:

..  math::   
   \Delta p=c_{d}\frac{\rho v^{2}}{2},

where :math:`c_{d}` is the flow drag coefficient. For pipes the drag coefficient depends on the pipe geometry and the *Darcy friction factor* :math:`\zeta` [Wikip-DFF]_:

.. math::   
   c_{d}=\zeta\frac{L}{d_i}
   
where :math:`L` is the length of the pipe and :math:`d_i` is the internal diameter of the pipe.

The friction factor depends on the Reynolds number :math:`Re={\rho v d}/{\mu}` and the relative surface roughness :math:`\varepsilon/d`. It can be determined using the *Moody chart*

|

.. figure:: /static/ThermoFluids/img/MoodyDiagram.jpg
   :width: 90%
   :align: center
   
   Moody chart


In the laminar region the friction factor depends only on the Reynolds number:

.. math::   
   \zeta = \frac{64}{Re}

In the turbulent region the relation is more complex and is given by the *Colebrook* equation [Colebrook39]_:

.. math::
   \frac{1}{\sqrt{\zeta}} = -2.0 \log_{10} \left(\frac{\epsilon/d_i}{3.7} + {\frac{2.51}{Re \sqrt{\zeta} } } \right)
   
In the limit of high Reynolds numbers the friction factor depends solely on the relative surface roughness.
   
As the *Colebrook* correlation is implicit in :math:`\zeta`, it is not suitable for direct calculations. 
Different approximations have been developed amongst which special attention deserves the *Churchill* correlation [Church77]_, which covers 
all flow regimes: laminar, transitional and turbulent:

..  math::
   \zeta =  8\left[\left(\frac{8}{Re}\right)^{12}+\frac{1}{\left(\Theta_{1}+\Theta_{2}\right)^{1.5}}\right]^{\frac{1}{12}}
   
   \Theta_{1}  =  \left[2.457\cdot\ln\left(\left(\frac{7}{Re}\right)^{0.9}+0.27\frac{\varepsilon}{d_i}\right)\right]^{16}
   
   \Theta_{2}  =  \left(\frac{37530}{Re}\right)^{16}
 

-------------
Heat Exchange
-------------
 
----------
References
----------
 
 
.. [Wikip-DFF] http://en.wikipedia.org/wiki/Darcy_friction_factor_formulae
   
.. [Church77] Churchill, S.W. (November 7, 1977). "Friction-factor equation spans all fluid-flow regimes". 
   Chemical Engineering: 91–92.
   
.. [Colebrook39] Colebrook, C.F. (February 1939). "Turbulent flow in pipes, with particular reference to the 
   transition region between smooth and rough pipe laws". Journal of the Institution of Civil Engineers (London).
