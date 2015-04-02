===================
The SmoWeb platform
===================

--------
Overview
--------

SmoWeb is an *open source web computational platform* developed in *Python* 
and a library of *applications* built on top of this platform.

**Computational Platform**
--------------------------
It provides the infastructure for rapid development of scientific
applications with graphical user interface.

**Web platform**
----------------
It runs on the web and does not require installation of any software
by the user. All the computations are performed in the cloud.
   
**Open source**
---------------
The platform can be used under GPL_ v.3 open source license, 
allowing anyone to use our code at their will; developers can read, review, modify or 
contribute code to the platform or develop their own version of the platform,
provided that they comply with the copyleft restrictions of the GPL licence.
Alternative licensing schemes can be negotiated. More information about it
can be found `here </?model=License>`_.

**Python/Cython**
-----------------
Python was chosen as the implementation language because it is a powerful
modern general purpose object-oriented language. Today it has
become an inseparable part of scientific computing, due to the vast 
abundance of open source python libraries and interfaces to major
software tools. Cython is a Python extension, allowing to speed up critical parts
of the software and providing easy interfacing to C/C++/Fortran libraries.

**SmoWeb Applications**
-----------------------

A number of applications have already been developed and are continously
being developed on top of the fucntionality provided by the platform. Currently
these are mostly in the fields of thermodynamics, heat and fluid flow, and
transient bio-system modeling. Although the platform is suitable for any kind
of engineering modeling and simulation, the main focus is on system and process
engieering.
   
|

If you are curious about the implementation of SmoWeb, check out the project's `documentation </static/doc/html/index.html>`_

----------
SmoWeb 1.0
----------

Platform
--------

* **Model definition** consists of interface definition and computational implementation:

  * a NumericalModel is defined in python code with input and output fields
  * fields can be a physical quantity (with units), boolean, text, choice, record array, data array, etc.
  * models can be inherited (expanded) or included as submodels in other models
  * fields can be grouped in field groups, and field groups in super-groups to form a model view
  * each NumericalModel has at least a single ``compute`` method, which can be arbitrarily complex,
    and uses the full power of Python language and all installed libraries 

* Automatic **graphical user interface** for the web browser
   
  * no html, javascript or css necessary; comes out of the box with the model definition
  * a model can send model views with data to the browser
  * hierarchical representation of the model with dialog groups and tabs
  * numerical, boolean, text fields; choice selections from dropdown menus
  * advanced editors for complex data structures (e.g. record array)
  * the user interacts with the browser to edit the model values
  * physical quantity editors have built-in unit conversion  
  * at the click of a button, the user can send data back and request the server to 
    perform a number of predefined model actions
  * results from calculations are sent to the user for inspection
  * simple fields, plots, tables and diagrams in the results
   
* Advanced **data storage**:

  * model values can be automatically saved and retrieved from a database
  * a unique link is generated for a saved model, and can be used to share model data
  * schema-less Mongo database: automatic storage for any data structure defined 
  * HDF5/Pandas storage for time series and other array data

* Integration of numerous **computational libraries and frameworks**:

  * NumPy_, SciPy and MatPlotLib, the standard python libraries for numerical computation and 
    visualization, with much of the basic functionality present in Matlab.
  * CoolProp_: *property database* with wide range of common and refrigerant fluids including 
    gas, liquid and two-phase properties  
  * Assimulo_ + CVODE_: library for simulating *dynamical system models* (models based on hybrid 
    systems of non-linear ordinary differential equations with events/discontinuities) 
  * PyDDE_: library for simulating dynamical systems described 
    by *differential equations with delays*.
  * FiPy_: library by NIST for modeling heat and mass transfer in 1, 2, and 3D geometries based
    on the Finite Volume Method 

Models and applications
-----------------------

* Thermo-fluids
   
  * Property calculators
  * Pipe flow
  * Convectional heat exchange
  * Thermodynamic cycles
  * 1D heat exchange examples

* Bio-reactors

  * Chemostat models


----------
SmoWeb 2.0
----------
This is the current development plan for the next version of SmoWeb. We have deliberately planned
more things than we will be able to implement, and will later select a subset of them based on the available resources


Platform
--------

* Integration of Celery, a **distributed task queue**

  * long running simulation tasks will be executed in the background
  * users will be updated continuously about the progress of the simulation

* Dynamical simulation environment

  * component and system model definitions in python
  * generation of C/C++ code for simulation speed-up
  * graphical system editor (like Simulink, or the Modelica-based GUI tools Dymola and SimulationX)
  * (?) Modelica integration
  * advanced result viewer 

* Parameter variation/optimization

  * design of experiments
  * parameter sensitivity
  * optimization

* User authentication and access control

Models and applications
-----------------------

* Thermo-fluid modules

  * more material models
  * mixtures
  * advanced cycles
  * user defined systems
  
* Bio-reactor modules
  
  * Advanced fermentation model

* Chemical process modules (integration of Cantera_)
* HVAC modules (energy management of buildings)
* Renewable energy modules (solar heating etc.)

.. _NumPy: http://www.numpy.org/
.. _CoolProp: http://www.coolprop.org/
.. _Assimulo: http://www.jmodelica.org/assimulo
.. _CVODE: https://computation.llnl.gov/casc/sundials/description/description.html
.. _FiPy: http://www.ctcms.nist.gov/fipy/
.. _PyDDE: https://github.com/hensing/PyDDE
.. _Cantera: http://www.cantera.org/docs/sphinx/html/index.html
.. _GPL: https://www.gnu.org/copyleft/gpl.html
