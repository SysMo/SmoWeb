=================================
Object creation and serialization
=================================

----------------
Numerical models
----------------

Metaclass
---------

Numerical models are created by subclassing the abstract :class:`~smo.model.model.NumericalModel` class. A metaclass,
:class:`~smo.model.model.NumericalModelMeta`, facilitates the creation by collecting all class attributes of the model 
into dictionary attributes ``declared_fields``, ``declared_submodels``, ``declared_attrs``, ``declared_basicGroups``, 
``declared_superGroups``, ``declared_modelViews``, which it also updates with the respective
dictionaries of the inherited numerical models. Inherited submodels, field-groups, view-groups, supergroups and
model views are used in the inheriting class by including their names as strings.

Instantiating numerical models
------------------------------
When an instance of a numerical model is created, the fields from ``declared_fields``
are set as attributes of the instance and assigned defalut values. The submodels from ``declared_submodels`` 
are also instantiated at this point.

Serialization of numerical models
---------------------------------

The :func:`modelView2Json` method of a :class:`~smo.model.model.NumericalModel` instance
is used for serialization of its views - the values of its :class:`~smo.model.fields.ModelView` attributes - 
by creating a JSON representation of the view it is applied to, including its definition, the values of the fields it contains 
and the actions associated with it. The JSON object takes the form::

   {'definitions': definitions, 'values': fieldValues, 'actions': actions}
   
where the ``definitions`` property contains the view's definition, the ``values`` property represents the values of 
the fields in the view and ``actions`` is a serialization of its actions. 


------------
Modular page
------------

Modular page views subclass the :class:`~smo.web.view.ModularPageView` class. A sample definition of a 
page view is given below::
   
   router = ViewRouter('ThermoFluids', ThermoFluids)
   
   @registerView(router)
   class FluidPropsCalculatorView(ModularPageView):
      name = 'FluidPropsCalculator'
      label = 'Fluid properties (CoolProp)'
      modules = [FluidProperties, FluidInfo, SaturationData, FluidPropertiesDoc]
      requireJS = ['dygraph', 'dygraphExport']
      requireGoogle = ['visualization']
      
      @action.post() 
      def computeFluidProps(self, model, view, parameters):    
         fpc = FluidProperties()
         fpc.fieldValuesFromJson(parameters)
         fpc.compute()
         if (fpc.isTwoPhase == True):
            return fpc.modelView2Json(fpc.resultViewIsTwoPhase)
         else:
            return fpc.modelView2Json(fpc.resultView)

The page view *FluidPropsCalculatorView* is registered with the ViewRouter ``router`` and its method :func:`computeFluidProps` is converted to a 
:class:`~smo.web.view.PostAction` object using the  ``@action.post()`` decorator.

Metaclass
---------

The metaclass, :class:`~smo.web.view.ModularPageViewMeta`, loops over the modular page view class' attributes, 
as well as the attributes of all its base classes, collecting the post actions, lists of names of JavaScript libraries and 
lists of names of Google modules required to render the page respectively in ``postActions``, ``requiredJSLibraries`` and ``requiredGoogleModules`` 
attributes of the page view class being created. When the static page is rendered by the template engine later, the URLs of the
JavaScript lbraries and parameters for loading Google modules are obtained from the :class:`~smo.web.view.ModularPageView` class'
respective registries based on the names contained in the ``requiredJSLibraries`` and ``requiredGoogleModules`` sets. The metaclass
also sets a default ``controllerName`` attribute of the page view if missing, used in the AngularJS app as part of the webpage.

Instantiation
-------------

Page view objects are created by the :func:`view` method of the router instance that the 
page view class is registered with. The router's :func:`view` method then passes the HTTP request for processing to the 
page view object's own :func:`view` method.
  