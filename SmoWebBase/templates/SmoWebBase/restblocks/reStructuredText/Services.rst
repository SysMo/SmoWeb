========
Services
========

.. contents:: Table of Contents

.. |ExampleAMESimCircuit| image:: /static/img/sysmo/AmeSimExampleCircuit1.png
   :height: 200px

.. |ExampleAMESimResult| image:: /static/img/sysmo/AmeSimExampleCircuit1_Result.png
   :height: 200px

-----------------------
Dynamical system models
-----------------------

We can model complex circuits in the thermal, fluid, mechanical, electrical and other domains. 
These simulations are typically transient, showing the development of various system variables over time. 
The CO2 heat pump shown here, for example, consists of a compressor, condenser, expansion valve, evaportor 
and a recurperator (a counterflow heat exchanger). The different componnent are laid out graphically, 
and interconnected. After the simulation run, some results are shown on the graph. In this case we 
were interested in the temperatures at the different parts of the system.

.. class:: align-center subfigures

+------------------------+-----------------------+
| |ExampleAMESimCircuit| | |ExampleAMESimResult| |
|                        |                       |
| Heat pump circuit      | Results               |
+------------------------+-----------------------+

The component used in system simulations are taken from various libraries of componets. These can include 
individual software libraries (e.g. AMESim Thermal Library) or standard libraries (Modelica Standard Library). 
Sometimes, however, no component exists for the particular need. In this case we can develop a new component 
model based on analytical physical model, empirical correlations or interpolation. The models canbe developed 
either in C/C++ or in the Modelica language.

----------------------------------------
Finite Element / Finite Volume 3D models
----------------------------------------

When heat exchange processes, mechanical stresses or fluid flow occur in an object of complex geometry, 
the only way to accurately predict the object behaviour is to use some form of FEM (finite element model). 
The geometrical object (or objects) has to be partitioned into simple elements (e.g. tetrahedrals, prisms or 
hexahedrals, triangles, quadrangles etc). The FEM solver finds approximate solution to the partial differential 
equations at discrete point (the vertices of the elements), and interpolates (linear, bilinear, quadratic etc.) 
within the elements.

.. figure:: /static/img/sysmo/EngineThermal.png
   :width: 50%
   :align: center

Thermal finite element/volume modeling
--------------------------------------

Thermal FEM is used when heat exchange processes and resulting temperatures are of interest.

Features
   * Heat conduction in solid volumes
   * Radiation between solid surfaces (important at high temperatures or in vacuum)
   * Fixed temperature, fixed heat flow or convection boundary conditions

Sometimes it is not the temperatures, but rather the integral heat fluxes are of interest. In this case using
the standard FEM method may yield incorrect results, as it is not conservative in general. That is, the net heat
balance through all the surfaces may turn out to be non-zero (it will approach zero as the mesh gets finer, but 
at the cost if increased computational time). In this case, a low order FEM method called FVM (finite volume method) 
can be used. (e.g. see SmoFlow Thermal Solver). The temperature values resulting from FVM may not be as accurate, 
but the heat fluxes are guaranteed to be conserved.

.. figure:: /static/img/sysmo/EngineHead_Temperature.png
   :width: 50%
   :align: center

Mechanical finite element modeling
----------------------------------

Mechanical FEM is typically used to find the critical stresses in a component as a result of mechanical loads.
Because stresses are high order quantities (depend on the derivative of the displacement), higher order FEM 
method is usually used (e.g. quaratic interpolation in space). Some materials are also anisotropic (that is, 
stronger in one direction, than in others), which complicates additionally the calculation.

There are two different types of mechanical analysis:
   * Steady state: constant loads/displacements are applied to the component. Results are stresses/strains
   * Eingenmode (resonant) : oscillating loads are applied to the component. Results are stresses/strains and resonant frequencies

Software
   * `ANSYS Multiphysics`_ (commercial)
   * `Abaqus`_ (commercial)
   * `ElmerFEM`_ (open-source)
   * `SfePy`_ (open-source)


.. figure:: /static/img/sysmo/EngineHead_Displacement.png
   :width: 50%
   :align: center

Computational Fluid Dynamics (CFD)
----------------------------------
Fluid processes modeling is an absolute necessity in many egineering designs. Pressure drop, heat exchange,
separation and  mixing are complex phenomena, affecting the performance of pumps, valves, turbines, reaction 
chambers and many other systems. A modification of FEM, called Finite Volume Method, is typically used to describe
the transport of mass, momentum, energy, turbulence etc. occuring in fluids.

Software
   * `AnsysCFX`_ (commercial)
   * `OpenFOAM`_ (open-source)
   
Other Finite Volume Tools
-------------------------

Although the finite volumes method is primarily used for fluid flow, it is applicable to every problem which
involves transport of mass and energy. Multiphysics models involving heat exchange, diffusion and advection 
of materials often use finite volume models too.

Software
   * `FiPy`_ (open-source)

Pre- and post-processing
------------------------
Whether commercial or open source sofware is used, the steps involved in the solution process are quite the same. 
First a mesh is created in order to partition the component geometry. Then the mesh is used as input to the solver 
together with additional user input (material properties, boudary conditions, initial conditions etc.). Finally 
the results from the solver are inspected and processed to extract valuable data (e.g. temperature at a given point, 
heat flux at a boundary, position and value of the maximal stress etc.).

Various software tools can be used in the pre- and post-processing steps. Each commercial software typically has
its own tools (e.g. CFX Pre and CFX Post). There are some "standard" open-source tools which are used by many solvers.
For mesh generation the `Salome platform`_ (integrating many different meshing algorithms) or `GMSH`_ can be used. 
For post-processing `ParaView`_ is the de-facto standard. (Mayavi2 is another alternative, also based on the Visualization Toolkit - VTK)

.. _Abaqus: http://www.3ds.com/products-services/simulia/products/abaqus/
.. _ElmerFEM: https://www.csc.fi/web/elmer
.. _`ANSYS Multiphysics`: http://www.ansys.com/Products/Simulation+Technology/Multiphysics
.. _AnsysCFX: http://www.ansys.com/Products/Simulation+Technology/Fluid+Dynamics/Fluid+Dynamics+Products/ANSYS+CFX
.. _OpenFOAM: http://www.openfoam.com/
.. _FiPy: http://www.ctcms.nist.gov/fipy/
.. _GMSH: http://geuz.org/gmsh/
.. _`Salome platform`: http://www.salome-platform.org/
.. _ParaView: http://www.paraview.org/
.. _SfePy: http://sfepy.org/doc-devel/index.html
