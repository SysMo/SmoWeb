=================================
Object creation and serialization
=================================

----------------
Numerical models
----------------

Numerical models are created by subclassing the abstract :class:`~smo.model.model.NumericalModel` class. A metaclass,
:class:`~smo.model.model.NumericalModelMeta`, facilitates such creation by collecting all class attributes of the model 
into a dictionary attribute *declared_fields*, which it also updates with the *declared_fields*
dictionaries of all inherited numerical model classes. Base class fields are used in field- and view-groups
of the subclass by including their names as strings, which are then resolved by :class:`~smo.model.model.NumericalModelMeta`.
The metaclass also sets *name*, *label* and *title* attributes, as well as *showOnHome* attribute, used to specify 
if a thumbnail of the model is to be displayed on the home page, if such attributes were not set in the class definition. 