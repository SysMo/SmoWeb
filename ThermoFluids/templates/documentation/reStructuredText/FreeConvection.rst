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
| :math:`\beta=\frac{1}{\rho}\left(\frac{\partial\rho}{\partial T}\right)_{p}` | isobaric thermal expansion coefficient      |
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

The following steps are taken to compute the convective heat exchange:

1. Compute the fluid properties
2. Determine the characteristic length and surface area for the particular geometry configuration
3. Compute the Grasshof number
4. Compute the Rayleigh number
5. Determine whether laminar or turbulent flow occurs
6. Use the appropriate Nusselt number correlation to compute the :math:`Nu=f\left(Ra,Pr\right)`
7. Compute the convection coefficient

.. math::
   \alpha=\frac{Nu\cdot\lambda}{s}
   
8. Compute the heat flow rate

.. math::
   \dot{Q}=\alpha\cdot A\cdot\Delta T


-------------
External Flow
-------------

The following geometry configurations have been implemented for external free convection:
  

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
:math:`Ra_{\alpha}=Ra\cdot \cos (\alpha)` for :math:`Ra`.

""""""""""""""""""""""""""""""""""""""""""""""""""
Top side of hot plane or bottom side of cold plane
""""""""""""""""""""""""""""""""""""""""""""""""""
At low :math:`Ra` the same holds: substitute :math:`Ra_{\alpha}=Ra\cdot\cos(\alpha)` for :math:`Ra`
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
| Shape     | Parameter                         | Description           |
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

Once again there are two cases:

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

-------------
Internal Flow
-------------

The following geometry configurations have been implemented for internal free convection:
  

Vertical planes
---------------

.. class:: nice-table

+---------------+-------------------------+
| Parameter     | Description             |
+===============+=========================+
| :math:`h`     | height                  |
+---------------+-------------------------+
| :math:`w`     | width                   |
+---------------+-------------------------+
| :math:`d`     | distance between planes |
+---------------+-------------------------+
| :math:`s = d` | characteristic length   |
+---------------+-------------------------+

If 

.. math::
   \frac{h}{s}<80 
   
for 

.. math::
   10^{4}<Ra<10^{7}
   
then

.. math::
   Nu=0.42\cdot Pr^{0.012}\cdot Ra^{0.25}\left(\frac{h}{s}\right)^{-0.25}

while for 

.. math::
   10^{7}<Ra<10^{9}

the Nusselt number is derived from
 
.. math::
   Nu=0.049\cdot Ra^{0.33}

In the case of 

.. math::
   Ra>10^{9}
   
the Nusselt correlation is unknown.

Inclined planes
---------------

.. class:: nice-table

+----------------+---------------------------------------------------------------------------------------+
| Parameter      | Description                                                                           |
+================+=======================================================================================+
| :math:`l`      | length (inclined)                                                                     |
+----------------+---------------------------------------------------------------------------------------+
| :math:`w`      | width                                                                                 |
+----------------+---------------------------------------------------------------------------------------+
| :math:`d`      | distance between planes                                                               |
+----------------+---------------------------------------------------------------------------------------+
| :math:`\alpha` | inclination angle (:math:`\alpha = 0` vertical, :math:`\alpha = 90^\circ` horizontal) |
+----------------+---------------------------------------------------------------------------------------+
| :math:`s = d`  | characteristic length                                                                 |
+----------------+---------------------------------------------------------------------------------------+

There are two cases:

"""""""""""""""""""""""""""
Heat is transmitted upwards
"""""""""""""""""""""""""""

.. math::
   Nu=C\cdot Ra^{0.33}\cdot Pr^{0.074}

where :math:`C` is determined from :math:`\alpha` based on the following values:

.. class:: nice-table

+------------------+-------------------------+
| :math:`\alpha`   | :math:`C`               |
+==================+=========================+
| :math:`0^\circ`  | :math:`4.9\cdot10^{-2}` |
+------------------+-------------------------+
| :math:`30^\circ` | :math:`5.7\cdot10^{-2}` |
+------------------+-------------------------+
| :math:`45^\circ` | :math:`5.9\cdot10^{-2}` |
+------------------+-------------------------+
| :math:`60^\circ` | :math:`6.5\cdot10^{-2}` |
+------------------+-------------------------+
| :math:`90^\circ` | :math:`6.9\cdot10^{-2}` |
+------------------+-------------------------+


"""""""""""""""""""""""""""""
Heat is transmitted downwards
"""""""""""""""""""""""""""""
If 

.. math:: 
   5\cdot10^{3}<Ra<10^{8}
   
for 

.. math::
   \alpha=45^{\circ}

the Nusselt number is calculated from the formula

.. math::
   Nu=1+\frac{0.025\cdot Ra^{1.36}}{Ra+1.3\cdot10^{4}}
   
In the other cases, the Nusselt correlation is unknown.

Horizontal planes
-----------------

.. class:: nice-table

+---------------+-------------------------+
| Parameter     | Description             |
+===============+=========================+
| :math:`l`     | length                  |
+---------------+-------------------------+
| :math:`w`     | width                   |
+---------------+-------------------------+
| :math:`d`     | distance between planes |
+---------------+-------------------------+
| :math:`s = d` | characteristic length   |
+---------------+-------------------------+

For 

.. math::
   Ra>Ra_{c}\left(Ra_{c}=1708\right) 
   
if 

.. math::
   1708<Ra<2.2\cdot10^{4}

the Nusselt number is determined by the correlation

.. math::
   Nu=0.208\cdot Ra^{0.25}
  
while for 

.. math::
   Ra<2.2\cdot10^{4}
   
it can be obtained using the formula

.. math:: 
   Nu=0.092\cdot Ra^{0.33}

For 

.. math::
   Ra<Ra_{c}\left(Ra_{c}=1708\right)
    
no convection occurs. Heat exchange is purely by conduction.

Horizontal annuli
-----------------

.. class:: nice-table

+-------------------------+-----------------------+
| Parameter               | Description           |
+=========================+=======================+
| :math:`l`               | length                |
+-------------------------+-----------------------+
| :math:`r_{i}`           | inner radius          |
+-------------------------+-----------------------+
| :math:`r_{o}`           | outer radius          |
+-------------------------+-----------------------+
| :math:`s = r_{o}-r_{i}` | characteristic length |
+-------------------------+-----------------------+

For 

.. math::
   Ra>7.1\cdot10^{3}
   
if

.. math::
   \frac{r_{o}}{r_{i}}\leqq8

and if heat is transmitted outwards, the Nusselt correlation is:

.. math::
   Nu=0.2\cdot Ra^{0.25}\cdot\left(\frac{r_{o}}{r_{i}}\right)^{0.5}
  
In the other cases, the Nusselt correlation is unknown.

----------
References
----------

.. [HeatAtlas] VDI (Verein Deutscher Ingenieure), Heat Atlas, Springer-Verlag, 2010, Part F: Free convection
   
   







 