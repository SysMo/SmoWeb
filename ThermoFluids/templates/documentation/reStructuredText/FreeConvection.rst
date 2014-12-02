.. sectnum::
   :suffix: .

===============
Free Convection
===============

-------------
External Flow
-------------

Parameters
----------

A geometry configuration among the following can be selected:

* vertical plane
* inclined plane top
* inclined plane bottom
* horizontal plane top
* horizontal plane bottom
* vertical cylinder
* horizontal cylinder
* sphere
* finned pipe
* convection coefficient

where the *convection coefficient* option allows for calculating the heat flow rate directly from a user input for 
the convection coefficient.

The thermal inputs include the surface temperature of the solid body (:math:`T_{s}`) and the fluid temperature far from the surface (:math:`T_{\infty}`).
The computation can be done either at :math:`T_{s}` or the mean temperature :math:`T_{*}=\frac{1}{2}\left(T_{s}+T_{\infty}\right)` and is also customizable by an input for the heat exchange gain factor.  

The convection coefficient :math:`\alpha` is calculated from the formula:
 
.. math::
   \alpha=\frac{Nu\cdot\lambda}{L}

where :math:`Nu` is the Nusselt number, :math:`\lambda` is the thermal conductivity, and :math:`L` is the characteristic length.
The latter is determined for each specific geometry configuration as follows:

* :math:`h` for vertical plane, inclined plane and vertical cylinder
* :math:`d` for horizontal cylinder and sphere
* :math:`\frac{d}{4}` for a horizontal plane with a circular shape 
* :math:`\frac{w\cdot l}{2\left(w+l\right)}` for a horizontal plane with a rectangular shape
* :math:`d+h_{f}` for finned pipe

The heat flow rate :math:`\dot{Q}` is then derived from the formula:

.. math::
   \dot{Q}=\alpha\cdot A\cdot\Delta T
 
where :math:`A` is the surface area of the solid body and :math:`\Delta T` is the temperature difference.
 
The Nusselt number :math:`Nu` is determined for each configuration by a specific :math:`Nu=f\left(Ra,Pr\right)` correlation,
where :math:`Ra` is the Rayleigh number and :math:`Pr` is the Prandtl number:
 
^^^^^^^^^^^^^^
Vertical plane
^^^^^^^^^^^^^^

.. math::
   Nu=\left\{ 0.825+0.387\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{6}}\right\} ^{2}

where
 
.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.492}{Pr}\right)^{\frac{9}{16}}\right]^{-\frac{16}{9}}
 
^^^^^^^^^^^^^^^^^
Vertical cylinder
^^^^^^^^^^^^^^^^^

.. math::
   Nu=Nu_{plate}+0.97\frac{h}{d}
 
where :math:`Nu_{plate}` is the Nusselt number for a vertical plate with height :math:`h`

^^^^^^^^^^^^^^
Inclined plane
^^^^^^^^^^^^^^

Let :math:`\alpha` be the angle of inclination to the vertical. The are two cases:

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
The surface transmits heat downward or absorbs heat from above
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
In the equation for vertical plane :math:`Ra_{\alpha}=Ra\cdot \cos (\alpha)` is substituted for :math:`Ra`.

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
The surface transmits heat upward or absorbs heat from below
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. math::
   Nu=0.56\left(Ra_{c}\cdot \cos (\alpha)\right)^{\frac{1}{4}}+0.13\left(Ra^{\frac{1}{3}}-Ra_{c}^{\frac{1}{3}}\right)
 
where :math:`Ra_{c}` is derived from 

.. math::
   Ra_{c}=10^{\left(8.9-0.00178\cdot\alpha^{1.82}\right)}
 
^^^^^^^^^^^^^^^^
Horizontal plane
^^^^^^^^^^^^^^^^
There are two cases:

""""""""""""""""""""""""""""""""""""
Heat is emitted at the upper surface
""""""""""""""""""""""""""""""""""""
If

.. math::
   Ra\cdot f_{1}\left(Pr\right)<7\cdot10^{4}
   
then

.. math::
   Nu=0.766\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{5}}

Otherwise

.. math::
   Nu=0.15\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{3}}

where

.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.322}{Pr}\right)^{\frac{11}{20}}\right]^{-\frac{20}{11}}
 


""""""""""""""""""""""""""""""""""""
Heat is emitted at the lower surface
""""""""""""""""""""""""""""""""""""
.. math::
   Nu=0.6\left[Ra\cdot f_{1}(Pr)\right]^{\frac{1}{5}}

on condition that 

.. math::
   10^{3}<Ra\cdot f_{1}\left(Pr\right)<10^{10}

where

.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.492}{Pr}\right)^{\frac{9}{16}}\right]^{-\frac{16}{9}}

^^^^^^^^^^^^^^^^^^^
Horizontal cylinder
^^^^^^^^^^^^^^^^^^^
.. math::
   Nu=\left\{ 0.60+0.387\left[Ra\cdot f_{1}\left(Pr\right)\right]^{\frac{1}{6}}\right\} ^{2}

where

.. math::
   f_{1}\left(Pr\right)=\left[1+\left(\frac{0.559}{Pr}\right)^{\frac{9}{16}}\right]^{-\frac{16}{9}}
 
^^^^^^
Sphere
^^^^^^
.. math::
   Nu=0.56\left[\left(\frac{Pr}{0.846+Pr}\right)Ra\right]^{\frac{1}{4}}+2
 
^^^^^^^^^^^
Finned pipe
^^^^^^^^^^^
.. math::
   Nu=0.24\left(Ra\frac{b}{d}\right)^{\frac{1}{3}}

where :math:`b` is the fin spacing and :math:`d` is the diameter of the core pipe. The area used to
calculate the heat exchange rate is the total surface area of the core pipe and fins. 

----------
References
----------

"VDI Heat Atlas", Springer 








 