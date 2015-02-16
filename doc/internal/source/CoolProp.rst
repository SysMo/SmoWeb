==============================
CoolProp - available interface
==============================


.. module:: smo.media.CoolProp.CoolProp

.. autoclass:: Fluid

* Methods:

 * BibTeXKey
 * saturation_p
 * saturation_T

* Properties:

 * EOSReference
 * TransportReference
 * CAS
 * ASHRAE34
 * name
 * aliases
 * molarMass
 * accentricFactor
 * critical
 * tripple
 * fluidLimits
 
class **FluidState**:

* Methods:

 * isTwoPhase
 
 .. method:: update(bla, blah, blah)
 
 * update_Tp
 * update_Trho
 * update_prho
 * update_ph
 * update_ps
 * update_pq
 * update_Tq
 * getSatL
 * getSatV
 
* Properties:

 * T
 * p
 * rho
 * h
 * q
 * s
 * u
 * cp
 * cv
 * dvdp_T
 * dvdT_p
 * dpdt_v
 * dpdv_t
 * dpdrho_t
 * dpdt_sat
 * beta
 * mu
 * cond
 * Pr
 * gamma