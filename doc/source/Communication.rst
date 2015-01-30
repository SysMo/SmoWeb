===================================
Client-server communication process
===================================

------------
Page loading
------------

 * The client sends a GET request to the server containing the URL of the page e.g.
   ``http://platform.sysmoltd.com/ThermoFluids/FreeConvection/?model=FreeConvection_External&view=inputView&id=54cbb28b7dc7c734d92b16c6``
 * The application server receives the request and determines the path to the resource
   */ThermoFluids/FreeConvection*
 * The first part of the path *ThermoFluids* determines the application used for handling this URL
 * The rest of the path is the path of the page within the application. This can be handled differently based on the applicaton:
    * The application can have explicit list of URL addresses linking addresses to view-functions/view-classes
    * The application can have a registry of page views and use that registry to resolve the correspondng view-class
 * After the view-function/view-class is resolved it is called:
    * If the view-class is a subclass of :class:`~smo.django.view.ModularPageView`, its :func:`get` method is called and the request.GET parameters are processed.
      The :func:`get` method looks for three paremeters that uniquely define a set of values
      bound to a particular view of a numerical model:
    
       * model - used to specify the numerical model
       * view - used to specify the view of the numerical model
       * id - an id of a MongoDB record containing the set of values bound to the view
    
   