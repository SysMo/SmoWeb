===============
Numerical model
===============

---------------
Creating models
---------------

Numerical models are defined by subclassing the :class:`NumericalModel` class::

   from smo.model.model import NumericalModel
   from smo.model.fields import *

   class AreaCalculator(NumericalModel):
      ############# Inputs ###############
      width = Quantity('Length')
      length = Quantity('Length')
      geometryIn = FieldGroup([width, length], label = "Geometry")
      
      inputs = SuperGroup([geometryIn], label = "Inputs")
      
      ############# Results ###############
      area = Quantity('Area')
      geometryOut = FieldGroup([area], label = "Geometry")
      
      results = SuperGroup([geometryOut], label = "Results")
      
      ############# Methods ################
      def compute(self):
         self.area = self.width * self.length
         
The :class:`AreaCalculator` class defines 2 input fields (``width`` and ``length``) and one 
output field (``area``). The input fields are grouped in a field group with label ``Geometry``,
which is part of a super-group with label ``Inputs``. The outpu field ``area`` is part of 
a field group again with label ``Geometry`` (but a different one) which is part of the 
supergroup ``Results``. Finally a method :func:`compute` calculates the area from the
width and the length. The resulting user interface in the browser can be seen in the figure.

.. figure :: _static/img/area_calculator_ui.png
   :width:  400px
   :align: center

   User interface generated for the AreaCalculator class 

Available classes
-----------------

.. class:: NumericalModel 
   
   Abstract base class for numerical models.
   
---------------------------
Fields and field attributes
---------------------------

:class:`Field` - field base class
---------------------------------

Abstract base class for all the field types. Contains the common attributes for all 
fields:

 * label: the text label used in the user interface usually in front of the field
 
 * show: expression (as a string), which is evaluated on the client side and is used to 
   dynamically show and hide a field, based on the values of other fields. The
   other fields in the model are referenced by prefixing them with ``self.``

All the fields also contain a private ``_name`` attribute, which is the name used to declare 
the field. This attribute is crated in the constructor of :class:`NumericalModel`

:class:`Quantity`
-----------------

.. class::
   Represents 

:class:`String`
---------------

:class:`Boolean`
----------------

:class:`Choices`
----------------

:class:`RecordArray`
--------------------

:class:`ObjectReference`
------------------------

:class:`TableView`
------------------

:class:`PlotView`
-----------------


-------------------------------
Class fields vs instance fields
-------------------------------

----------------
Fields internals
----------------

.. method :: parseValue(value) 
   
   Check if the value is of valid type for this field type, and, if not, 
   attempts to convert it into one.
   For example if the Field is of type :class:`Quantity`\ ('Length') 
   then parseValue((2, 'mm')) will return 2e-3 (in the base SI unit 'm') which
   can be assigned to the field. Used implicitly by the :func:`__setattr__` method

.. method :: getValueRepr(value) 

.. method :: toFormDict() 
