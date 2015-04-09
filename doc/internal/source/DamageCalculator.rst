=================
Damage calculator
=================

-------------
Preprocessing
-------------

Stress calculator:

* Read stress tables (csv)
* Read P, T input files
* Calculate stresses
* Write stresses to files

TODO: Rewrite in C++:
 
 * Interpolators
 
---------------
Rainflow matrix
---------------

* compute percentiles
* locate extrema
* fill Rainflow matrix
* handle residual


------
Damage
------
* S-N curve parameters
* mean stress correction of the stress amplitudes
* compute damage

----------------
Multiaxial loads
----------------

Preprocessing

* Calculate stress tensor from look-up tables.

Afterwards

* Calculate main normal stresses.
* Calculate V=maximum main normal stress/minimum main normal stress.
* Scale all components of stress tensor with f=1+(1-k)*V (k=?)
* Transform stresses into cutting plane.
* Calculate equivalent stress. (how?)

* Rainflow-Counting.
* Damage calculation against Wöhler-curve.
* Find maximum damage value and according cutting plane and store it.

Questions

* Find out k for our material.
* Find out how equivalent stress is calculated.
* Check if we can use old Wöhler-curves.