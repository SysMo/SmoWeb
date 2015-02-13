=================
Modular page view
=================
.. module:: smo.django.view

-----------------------
Page structure overview
-----------------------

.. figure:: _static/server/img/pageorganizationalstructure.*
   :width: 600px

--------------
Creating pages
--------------
Modular page views are created by subclassing the :class:`ModularPageView` class::
   
   class HomeView(ModularPageView):
    name = "HomeView"
    label = "Home View"
    injectVariables = ['ModelCommunicator', 'variables']
    modules = [AreaCalculator, UnitConverterModule, Company]

A modular page consists of modules, which can be activated by the user by clicking on the corresponding pill
in the sidebar in the left of the page. 

.. figure:: _static/server/img/modular_page_view.png
   :width: 600px
   :align: center

   A modular page example
   
-------
Modules
-------

.. module:: smo.model.model

Page modules may be one of the following types:

:class:`NumericalModel`
-----------------------

.. figure:: _static/server/img/modular_page_view.png
   :width: 600px
   :align: center

   An active :class:`NumericalModel` module 


:class:`HtmlModule`
-------------------

.. autoclass:: HtmlModule

.. figure:: _static/server/img/unit_converter_module.png
   :width: 600px
   :align: center

   An active `HtmlModule` module 

:class:`RestModule`
-------------------

.. autoclass:: RestModule

.. figure:: _static/server/img/company_module.png
   :width: 600px
   :align: center

   An active `RestModule` module 
