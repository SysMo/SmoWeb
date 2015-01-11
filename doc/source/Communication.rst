===================================
Client-server communication process
===================================

--------------------
Initial page loading
--------------------

 * The client sends a GET request to the server containing the URL of the page e.g.
   *http://platform.sysmoltd.com/ThermoFluids/FreeConvection*
 * The application server receives the request and determines the path to the resource
   */ThermoFluids/FreeConvection*
 * The first part of the path *ThermoFluids* determines the application used for handling this URL
 * The rest of the path is the path of the page within the application. This can be handled differently based on applicaton:
    * The application can have explicit list of URL addresses linking addresses to view-functions
    * (TODO) The application can have a registry of page views and use that registry to resolve view-function
 * After the view-function/view-class is resolved it is called:
   * If the view-class is a subclass of ModularPageView