=================================
Object creation and serialization
=================================

----------------
Numerical models
----------------

Metaclass
---------

Numerical models are created by subclassing the abstract :class:`~smo.model.model.NumericalModel` class. A metaclass,
:class:`~smo.model.model.NumericalModelMeta`, facilitates such creation by collecting all class attributes of the model 
into a dictionary attribute ``declared_fields``, which it also updates with the ``declared_fields``
dictionaries of all inherited numerical model classes. Base class fields are used in field- and view-groups
of the subclass by including their names as strings, which are resolved by :class:`~smo.model.model.NumericalModelMeta` during the
class creation. The metaclass also sets ``name``, ``label`` and ``title`` attributes, as well as ``showOnHome`` attribute, used to specify 
if a thumbnail of the model is to be displayed on the home page, if such attributes were not set in the class definition.

Instantiating numerical models
------------------------------
When an instance of a numerical model class is created, the fields in the ``declared_fields`` dictionary attribute of the class
are set as attributes of the instance and assigned defalut values.

Serialization of numerical models
---------------------------------

The :func:`modelView2Json` method of a :class:`~smo.model.model.NumericalModel` instance
is used for serialization of its views - the values of its :class:`~smo.model.model.ModelView` attributes - 
by creating a JSON representation of the view it is applied to, including its definition, the values of the fields it contains 
and the actions associated with it. This is done by calling the :func:`superGroup2Json` method of the instance, 
which in turn calls :func:`fieldGroup2Json` and :func:`viewGroup2Json`, each responsible for the serialization of the segment 
of the hierarchical organization of the view it represents. In the :func:`fieldGroup2Json` and :func:`viewGroup2Json` methods, 
the definition of each field part of that field- or view-group is serialized by calling its :func:`toFormDict` method and its value is
added to the JSON object. The :func:`modelView2Json` method also loops over the actions of the view, 
calling their serialization method. The final JSON object takes the form::

   {'definitions': definitions, 'values': fieldValues, 'actions': actions}
   
where the ``definitions`` property contains the view's definition, the ``values`` property represents the values of 
the fields in it and ``actions`` is a serialization of its actions. 


------------
Modular page
------------

Metaclass
---------
