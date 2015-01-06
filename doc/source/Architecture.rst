============================
SmoWeb architecture overview
============================

.. figure :: _static/img/smoweb_components.svg
   :width: 1000px
   :align: center

   SmoWeb platform components

-------------------
Server architecture
-------------------

The server is responsible for performing most of the numerical compuations, saving and retrieving data
from the various storage backends, managing users and access. The server consists of a web server, 
application server with computational engine, data storages and task queue.

Web server
==========

The web-server provides the network communicaiton with the client. It 
redirects the client requests through a WSGI interface to the Python application
server and returns the responses back to the client. The communication with the 
client uses the HTTP protocol, but in the future will likely switch to the secure HTTPS
protocol.
Currently, Apache is used as the web-server, but there are many alternatives. 

Application server
==================

The application server (`Django`_) does the actual work and implements the platform business
logic. It accepts the client request, and based on its URL, calls a *view* (a 
function or a class designed to handle that particular request type). The view 
processes the parameters of the request, and itself calls classes and functions, 
part of the *Computational engine*, to perform the calculations. Finally, a response 
is formed based on the results of the computation and sent back to the client.

:ref:`More information <PageApplicationServer>`

Dynamic and static content
==========================

Dynamic content is the content based on Django views and is generated on the
fly based on the user input. Static content, on the other hand, consists of files
saved on the server, necessary for the proper display of the pages (CSS, 
JavaScript libraries, etc.). During the deployment phase of the applciation server, 
the static content is collected into a *static* folder and the contents of this folder
is served directly by the web server (Apache) to reduce the load on the application server.

Data storage
============

The platform stores and retrieves different kinds of data and for each there is a 
designated data storage backend:

 * Administration and user managamenet information is stored in a SQL relational 
   database.
   
 * Numerical models can be persisted in a non-relational database (MongoDB). They 
   are stored as *records* which do not have a predefined structure but use BSON (binary 
   JSON) format to store arbitrary hierarchical data. The actual structure of the data 
   is contained in the Python classes used as numerical models. Using non-relational DB
   allows for easy storage of a large number of different models. In contrast, relational DBs have
   well-defined tables and table columns and are suited for saving a large number of records
   having identical structure, and require special care when the Python model persisted is
   altered.
   
 * Large numerical arrays can be stored as *datasets* in HDF (Hierarchical Data Format)
   numerical database. HDF is suitable for storing a large amount of numerical data, allows
   for easy data extraction (like ranges and slices for multi-dimensional data), provides
   interface to numpy for performing numerical operations and allows compact data storage.
   
 * Finally, static content (CSS, Java Script, images etc.) is stored directly as files
   on the server file system.

:ref:`More information <PageDataStorage>`

Computational engine
====================

The computational engine is at the heart of the platform, this is where all the computational
apps are defined. At its top level, it consists of numerical models, classes which define 
input/output fields and field groups, as well as computational methods which operate on
these fields. The field definitions serve many purposes, including:
 
 * validation of field values
 * visualizing the fields to the client
 * storing and retrieving the field values in a database  

A number of external python libraries (numpy, scipy, 
pysparse, fipy, pyFMI etc.) and C/C++ libraries participate in the computational
process.

Asynchronous task scheduler
===========================
Small tasks, requiring little computational effort, are executed directly in the  
server process, while longer-running simulations are assigned to a task queue and executed
asynchronously. `Celery`_ is used as the task scheduler. During a long task execution,
the user receives information about the task progress.

-------------------
Client architecture
-------------------

The client provides the user interface, allowing the user to select computational applications,
enter data and visualize results.

Client requests
===============

During initial page load (that is, when a user clicks on an address link, or types a URL
in the address bar), a GET request is sent to the application server. The server response
is the back-bone HTML which gives the basic page layout (including the overhead navigation bar with
menu links, the sidebar with the different app modules and documenation present on this page,
and the elements outlining the app modules). During this stage are loaded all the necessary static
files providing formatting (CSS) and initialization (JS) of the page.

At the end of the load process, each app module on the page performs an AJAX request to the server, 
and based on the response contents, creates its user interface. Further actions in this module, may
trigger additional requests sending and receiving more data to/from the server (e.g. triggering a
computation, or storing/loading model data) and updating the user interface, while staying on the same page.

AngularJS application
=====================

The client applications are written using the `AngularJS`_ JavaScript framework by Google. 
AngularJS takes a MVC (model-view-controller) approach and facilitates the creation of 
interactive web pages with minimal code. Through the use of reusable modules and directives,
it allows for dynamic manipulation of the page HTML based on the interaction with the user.

.. _Celery: http://www.celeryproject.org/
.. _Django: https://www.djangoproject.com/
.. _AngularJS: https://angularjs.org/