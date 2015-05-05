=================
Damage calculator
=================


------------------------------------
Creating stress interpolation tables
------------------------------------

The script ``StressTablesXls2Hdf5.py`` creates stress interpolation tables reading data from Excel sheet and writing stress interpolation tables to a HDF5 file. The structure of stress interpolation table is the following:

* dataset (1D) T for temperatures
* dataset (1D) p for pressures
* 6 datasets (2D) s11, s12, s13, s22, s23, s33 for the 6 stresses

.. figure:: img/StressInterpolatorTableStructure.*
   :width: 800px
   
   Stress interpolation tables structure
   
------------------------------------
Running multiaxial damage calculator
------------------------------------

Stresses
--------




