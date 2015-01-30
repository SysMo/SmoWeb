========
Products
========

.. contents:: Table of Contents
   
-----------------
Software products
-----------------

SmoWeb
------

Online platform for engineering calculations and simulations. 
But if you are already here, you probably know what SmoWeb is.

SmoFlow
-------

.. figure:: /static/img/sysmo/SmoFlow3d_Icons.png
   :width: 80%
   :align: center

SmoFlow is a software developed to meet the demand for precision modeling of thermal and fluid processes. 

Features
~~~~~~~~

Solid and fluid models
   * solid material models
     
     * constant
     * temperature-dependent
   
   * fluid material models

     * constant properties
     * ideal gas 
     * table-defined properties
     * interface to CoolProp for complex analytical fluid models (including phase transitions)
   
1D fluid networks
   Components to model common fluid networks
      
   * chamber volumes
   * valves
   * pipes with heat exchange
   * fluid sources
   * property sensors

Heat exchange processes
   The library includes models for heat (and mass) exchange processes based on semiempiric correlations. 
   These include heat exchange in forced and free convection in various geometric configurations: 
   flow of fluid inside or outside a pipe, convection over a flat surface, flow in annular channels, 
   pipe immersed in a steady fluid, etc. Models are taken mainly from the VDI Heat Atlas (VDI Wärmeatlas).

Thermal solver
   Transient and steady state heat exchange processes in real-world 3D geometries can be computed using 
   the SmoFlow thermal solver. The geometry is represented by a mixed 1D (e.g. pipes), 
   2D (surfaces) and 3D (volumes) mesh. In a preprocessing step, the materials, 
   bodies and boundary condition types are defined and much of the heavy-weight calculations are done, 
   converting the 3D geometry into a system of material nodes and interactions between them. 
   Currently the solver can handle solid conduction, with multiple materials and temperature dependent material properties 
   (thermal radiation is next on the list). The thermal calculations are done using our own FEM solver
   (or rather a finite volume node-centered solver).

Implementation
~~~~~~~~~~~~~~

Open source, work in progress, prototype available. A completely open-source toolchain is available 
for the thermal solver:

* Salome for geomety creation (or import from STEP) and meshing
* SmoFlow thermal preprocessor for defining the thermal model on the mesh
* ParaView for postprocessing the results

FSM Controller Editor
---------------------

Finite State Machine controller is a controller which has a discreet predefined set of states. 
Think about a laundry machine - it can be soaking, washing, rinsing, filling water, pumping water out or centrifuging. 
At each moment only one of this modes of operation is activated, and there are criteria for switching to another one. 
For example::

   if filling level > max filling level then start heating water
   
   if water temperature > 50°C then start washing
   
   ........

Putting the control algorithm in some programming language (typically C) can be a very tedious task 
if there are many states and many conditions for transitions between them. 
For that purpose we have developed a GUI (graphical user interface), 
which allows in a systematic way to define the components of the controller:

* states
* conditions for state transitions
* actions on state entry
* actions on state exit
* output values, for state-dependent outputs

Once the controller is defined via the GUI, 
C-code can be automatically generated and compiled, resulting in an executable or dynamic library, 
ready to be integrated into the simulation.

The GUI is based on Eclipse and Eclipse EMF (Eclipse Modeling Framework).

.. figure:: /static/img/sysmo/FSMControler.png
   :width: 80%
   :align: center

FermA
-----
Ferma is a small Python application for managing small to medium-sized animal farms. 
It allows the user to enter and keep track of animal information, 
informs them of upcoming events related to individual animals and helps them keep all the important documentation 
in an electronic format for easy search and access. 

.. figure:: /static/img/sysmo/FermA-CowInfo.png
   :width: 80%
   :align: center

|
|
   
.. figure:: /static/img/sysmo/FermA-Report.png
   :width: 80%
   :align: center

Features
~~~~~~~~

* Keeps record of individual animals, as well as parent-children relations
* Keeps a health record of each animal, with any illnesses, treatments and treatment results
* Keeps track of the animal estrous cycles and warns the user when one is expected
* Keeps track of lactation information (the yield from each animal), allowing individual animal observation and selection
* Keeps track of feeding records, allowing the effect on milk yield to be analyzed
* Keeps electronic copies of each animal's passport and other important documents

Implementation
~~~~~~~~~~~~~~
The application is written in Python using Enthought Traits/TraitsUI. 
Traits is a framework for rapid application development, providing an out-of-the-box Model-View-Controller implementation. 
Traits takes care of the communication between the model classes and the user interface, 
so each time the user changes a value in the application window, the model is updated and vice versa.

The application data is stored in a text file in JSON format. 
This adds flexibility to the program, allowing to easily change the data structure.

-----------------
Hardware products
-----------------

Programmable thermostat
-----------------------

The thermostat uses a modular architecture which allows it to be used for a very basic application 
(controling a single temperature within a predefined range) or very advanced applications 
(observing, recording and controling  multiple temperatures with complex time-varying temperature profiles)

Features
~~~~~~~~

* Controls temperature (and optionally humidity)
* Can be used in a combined heating and cooling mode (activates a heater when temperature falls below a low threshold value, and a cooler when it rises above a high treshold value)
* Has an integrated real time clock (DS1307) and data logger, which can record temperature, humidity, etc. on an SD card
* Supports the Maxim 1-wire interface allowing an arbitrary number of temperature sensors (DS18B20) to be connected. DS18B20 is a high-resolution digital temperature sensor (0.0625°C when operating at 12-bit mode).
* Compatible with analog LM35 temperature sensors and DHT22 digital temperature/humidity sensors
* Can send sensor readings to a computer using a Serial-to-USB cable
* Integrated LCD and keypad for temperature observation and basic user control
* Fully reprogrammable, allowing custom configurations
* Based on the ATMega328 microcontroller unit (16 MHz, 32 kB program memory, 2 kB RAM). Can be upgraded to ATMega64xx or ATMega128xx MCU.
* Can communicate with external devices using the I2C or UART protocols.
* Open source hardware and software design

Implementation
~~~~~~~~~~~~~~

This is what the compact version of the controller looks like. 
You can see the power supply (top right, salvaged Nokia charger), the solid state relay (bottom right), 
the LCD screen & keypad. The microcontroller circuit is behind the keypad. 
Attached are one DS18B20 waterproof temperature sensor and one DHT22 temperature/humidity sensor

.. figure:: /static/img/sysmo/TemperatureController_v7.jpg
   :width: 50%
   :align: center
   
And this is the schematic of the Rev. 7 of the controller. You can download it also as a `pdf </static/img/sysmo/TemperatureController7_schem.pdf>`_

.. figure:: /static/img/sysmo/TemperatureController7_schem.svg
   :width: 50%
   :align: center