.. sectnum::
   :suffix: .
   :depth: 3

===============
Free Convection
===============

-------------------------
Free convection (general)
-------------------------

Parameters and variables
------------------------

.. class:: nice-table


+------------------------------------------------------------------------------+---------------------------------------------+
| Parameter                                                                    | Description                                 |
+==============================================================================+=============================================+
| :math:`g`                                                                    | earth acceleration (9.81 m/s :sup:`2`)      |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`T_s`                                                                  | surface temperature                         |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`T_\infty`                                                             | fluid temperature (far from the surface)    |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`p`                                                                    | fluid pressure                              |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`\mu`                                                                  | dynamic viscosity                           |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`\nu = \mu / \rho`                                                     | kinematic viscosity                         |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`c_p`                                                                  | specific heat capacity at constant pressure |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`\beta=\frac{1}{\rho}\left(\frac{\partial\rho}{\partial T}\right)_{p}` | isobaic thermal expansion coefficient       |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`\lambda`                                                              | thermal conductivity                        |
+------------------------------------------------------------------------------+---------------------------------------------+
| :math:`\alpha`                                                               | convection heat rate coefficient            |
+------------------------------------------------------------------------------+---------------------------------------------+

Dimensionless groups
--------------------

.. class:: nice-table

+------------------------------------------------+-----------------+-----------------------------------+
| Group                                          | Name            | Meaning                           |
+================================================+=================+===================================+
| :math:`Pr = \frac{c_p \mu}{\lambda}`           | Prandtl number  | ratio of momentum diffusivity     |
|                                                |                 |                                   |
|                                                |                 | to thermal diffusivity            |
+------------------------------------------------+-----------------+-----------------------------------+
| :math:`Gr =\frac{g s^3 \beta \Delta T}{\nu^2}` | Grashof number  | ratio of buoyancy forces          |
|                                                |                 |                                   |
|                                                |                 | to viscous forces                 |
+------------------------------------------------+-----------------+-----------------------------------+
| :math:`Ra = Gr\cdot Pr`                        | Rayleigh number |                                   |
|                                                |                 |                                   |
|                                                |                 |                                   |
+------------------------------------------------+-----------------+-----------------------------------+
| :math:`Nu = \frac{\alpha s}{\lambda}`          | Nusselt number  | ratio of convective heat transfer |
|                                                |                 |                                   |
|                                                |                 | to conductive heat transfer       |
+------------------------------------------------+-----------------+-----------------------------------+

Calculation algorithm
---------------------

The following steps are taken to compute the convective heat exchange

1. Compute fluid properties
2. Determine characteristic length and surface area for the particular geometry configuration
3. Compute Grasshof number
4. Compute Rayleigh number
5. Determine whether laminar or turbulent flow occurs
6. Use the appropriate Nusselt number correlation to compute the :math:`Nu=f\left(Ra,Pr\right)`
7. Compute convection coefficient

.. math::
   \alpha=\frac{Nu\cdot\lambda}{s}
   
8. Compute heat flow rate

.. math::
   \dot{Q}=\alpha\cdot A\cdot\Delta T


-------------
External Flow
-------------

The folowing geometry configurations have been implemented for external free convection
  

Vertical plane
--------------

.. class:: nice-table

+---------------+-----------------------+
| Parameter     | Description           |
+===============+=======================+
| :math:`h`     | height                |
+---------------+-----------------------+
| :math:`w`     | width                 |
+---------------+-----------------------+
| :math:`s = h` | characteristic length |
+---------------+-----------------------+

.. math::
   Nu=\left\{ 0.825+0.387\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{6}}\right\} ^{2}

where
 
.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.492}{Pr}\right)^{\frac{9}{16}}\right]^{-\frac{16}{9}}
 

Vertical cylinder
-----------------

.. class:: nice-table

+---------------+-----------------------+
| Parameter     | Description           |
+===============+=======================+
| :math:`h`     | height                |
+---------------+-----------------------+
| :math:`d`     | diameter              |
+---------------+-----------------------+
| :math:`s = h` | characteristic length |
+---------------+-----------------------+


.. math::
   Nu=Nu_{plate}+0.97\frac{h}{d}
 
where :math:`Nu_{plate}` is the Nusselt number for a vertical plate with height :math:`h`

Inclined plane
--------------

.. class:: nice-table

+----------------+---------------------------------------------------------------------------------------+
| Parameter      | Description                                                                           |
+================+=======================================================================================+
| :math:`l`      | length (inclined)                                                                     |
+----------------+---------------------------------------------------------------------------------------+
| :math:`w`      | width                                                                                 |
+----------------+---------------------------------------------------------------------------------------+
| :math:`\alpha` | inclination angle (:math:`\alpha = 0` vertical, :math:`\alpha = 90^\circ` horizontal) |
+----------------+---------------------------------------------------------------------------------------+
| :math:`s = l`  | characteristic length                                                                 |
+----------------+---------------------------------------------------------------------------------------+

There are two cases:

""""""""""""""""""""""""""""""""""""""""""""""""""
Top side of cold plane or bottom side of hot plane
""""""""""""""""""""""""""""""""""""""""""""""""""
The favorable pressure gradient stabilizes the boundary layer and pushes it towards the plate. 
The resulting Nusselt number can be obtained from the equation for vertical plane by substituting 
math:`Ra_{\alpha}=Ra\cdot \cos (\alpha)` for :math:`Ra`.

""""""""""""""""""""""""""""""""""""""""""""""""""
Top side of hot plane or bottom side of cold plane
""""""""""""""""""""""""""""""""""""""""""""""""""
At low :math:`Ra` the same holds: substitute :math:`Ra_{\alpha}=Ra\cdot \cos (\alpha)` for :math:`Ra`
in the equation for vertical plate. At :math:`Ra > Ra_{c}`, the adverse pressure gradient 
tends to cause boundary layer separation. In this case

.. math::
   Nu=0.56\left(Ra_{c}\cdot \cos (\alpha)\right)^{\frac{1}{4}}+0.13\left(Ra^{\frac{1}{3}}-Ra_{c}^{\frac{1}{3}}\right)
   
The critical Rayleigh number is a function of the angle :math:`\alpha` and is given by: 

.. math::
   Ra_{c}=10^{\left(8.9-0.00178\cdot\alpha^{1.82}\right)}
 
 
Horizontal plane
----------------

.. class:: nice-table

+-----------+-----------------------------------+-----------------------+
| sdsdfsdf  | Parameter                         | Description           |
+===========+===================================+=======================+
|           | :math:`l`                         | length                |
| Rectangle |                                   |                       |
|           | :math:`w`                         | width                 |
|           |                                   |                       |
|           | :math:`s = [l\cdot w]/[2(l + w)]` | characteristic length |
+-----------+-----------------------------------+-----------------------+
|           | :math:`d`                         | diameter              |
| Circle    |                                   |                       |
|           | :math:`s = d`                     | characteristic length |
|           |                                   |                       |
+-----------+-----------------------------------+-----------------------+

Once again there are two cases

""""""""""""""""""""""""""""""""""""""""""""""""""
Top side of hot plane or bottom side of cold plane
""""""""""""""""""""""""""""""""""""""""""""""""""

The fluid flow  is laminar for

.. math::
   Ra\cdot f_{1}\left(Pr\right)<7\cdot10^{4}
  
and turbulent otherwise. The Nusselt number is found from:

.. math:: 
   Nu=\begin{cases}
   0.766\cdot\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{5}} & \textrm{if flow is laminar}\\
   0.15\cdot\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{3}} & \textrm{if flow is turbulent}
   \end{cases}
 
where

.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.322}{Pr}\right)^{\frac{11}{20}}\right]^{-\frac{20}{11}}
 


""""""""""""""""""""""""""""""""""""""""""""""""""
Top side of cold plane or bottom side of hot plane
""""""""""""""""""""""""""""""""""""""""""""""""""

.. math::
   Nu=0.6\left[Ra\cdot f_{1}(Pr)\right]^{\frac{1}{5}}

on condition that 

.. math::
   10^{3}<Ra\cdot f_{1}\left(Pr\right)<10^{10}

where

.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.492}{Pr}\right)^{\frac{9}{16}}\right]^{-\frac{16}{9}}

Horizontal cylinder
-------------------

.. class:: nice-table

+---------------+-----------------------+
| Parameter     | Description           |
+===============+=======================+
| :math:`d`     | diameter              |
+---------------+-----------------------+
| :math:`l`     | length                |
+---------------+-----------------------+
| :math:`s = d` | characteristic length |
+---------------+-----------------------+

.. math::
   Nu=\left\{ 0.60+0.387\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{6}}\right\} ^{2}

where

.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.559}{Pr}\right)^{\frac{9}{16}}\right]^{-\frac{16}{9}}
 
Sphere
------

.. class:: nice-table

+---------------+-----------------------+
| Parameter     | Description           |
+===============+=======================+
| :math:`d`     | diameter              |
+---------------+-----------------------+
| :math:`s = d` | characteristic length |
+---------------+-----------------------+

.. math::
   Nu=0.56\left[\left(\frac{Pr}{0.846+Pr}\right)Ra\right]^{\frac{1}{4}}+2

Finned pipe
-----------

.. class:: nice-table

+-----------------------+------------------------------+
| Parameter             | Description                  |
+=======================+==============================+
| :math:`d`             | core pipe diameter           |
+-----------------------+------------------------------+
| :math:`h_f`           | fin height (above core pipe) |
+-----------------------+------------------------------+
| :math:`d_e = d + h_f` | effective diameter           |
+-----------------------+------------------------------+
| :math:`b`             | fin spacing                  |
+-----------------------+------------------------------+
| :math:`s = d_e`       | characteristic length        |
+-----------------------+------------------------------+

.. math::
   Nu=0.24\left(Ra\frac{b}{d}\right)^{\frac{1}{3}}

Note: the accuracy of the correlation is :math:`\pm 25\%`

----------
References
----------

.. [HeatAtlas] VDI (Verein Deutscher Ingenieure), Heat Atlas, Springer-Verlag, 2010, Part F: Free convection
   
   







 