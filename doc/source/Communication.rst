===================================
Client-server communication process
===================================

--------------------
Initial page loading
--------------------

 * The client sends a GET request to the server containing the URL of the page e.g.
   ``http://platform.sysmoltd.com/ThermoFluids/FreeConvection/?model=FreeConvection_External&view=inputView&id=54cbb28b7dc7c734d92b16c6``
 * The application server receives the request and determines the path to the resource
   */ThermoFluids/FreeConvection*
 * The first part of the path *ThermoFluids* determines the application used for handling this URL
 * The rest of the path is the path of the page within the application. This can be handled differently based on the applicaton:
    * The application can have an explicit list of URL addresses linking addresses to view-functions/view-classes
    * The application can have a registry of page views and use that registry to resolve the correspondng view-class
    
View resolution by router
-------------------------
  
 An instance of :class:`~smo.django.router.ViewRouter` is created for each application and is registered with a global registry
 of routers of the :class:`~smo.django.router.ViewRouter` class. The view-classes within an application are registered 
 with the corresponding router, allowing it to resolve requested page views.  
    
Processing GET requests
-----------------------
    
After the view-function/view-class are resolved, the view-function or the :func:`get` method of the view-class are called, 
respectively, and the request.GET parameters are processed. If the view-class is a subclass of :class:`~smo.django.view.ModularPageView`, 
the :func:`get` method looks for three paremeters that uniquely define a set of values bound to a particular view of a numerical model:
 * ``model`` - used to specify the numerical model or another type of page module
 * ``view`` - used to specify the view of a numerical model
 * ``id`` - an id of a MongoDB record containing the set of values bound to the view
Once the static page is loaded, POST requests are automatically sent to the server to fetch the data needed to visualize all 
numerical models that are displayed as modules on the particular page. 
 
-------------------------------------
AJAX requests via communicator object
-------------------------------------
 
After the initial page load, a communicator object at the client handles any further communication with the server. It sends 
AJAX requests specifying the actions that have to be carried out as well as the parameters needed for their execution. If the
communication is successful, the response data is kept at the communicator object for future use by the client. The communicator
is also responsible for signalling any communication and server errors to the client as well as delivering error messages. 
 
Types of POST actions:
 * *load* - used to load numerical model data  
 * *save* - used to save input data in MongoDB and generate a URL through which they can be loaded
 * custom actions - *compute*, to pefrom a computation, among others