=====
Setup
=====

-----------------------
User creation on server
-----------------------

Create the user with ``adduser``

---------------------------------------------------------------
Synchronizing virtual environment on local computer from server
---------------------------------------------------------------

* Add the two lines below at the end of the .bashrc file (*eg. /home/milen/.bashrc file*)::
   
   alias goVirtual="source /srv/VirtualEnv/SmoWebPlatform/bin/activate"
   alias cdSmoWeb="cd /data/Workspace/Django/django-example/SmoWeb"
      
* Create folder */srv/VirtualEnv* and */srv/SmoWeb/Log*

* Run in therminal::

   unison -ignore "Name {*.pyc}" /srv/VirtualEnv/ ssh://platform.sysmoltd.com//srv/VirtualEnv

-------------------------------
Setting up workspace in Eclipse
-------------------------------

* Create workspace SmoWeb (e.g. */data/Workspace/Projects/SysMo/SmoWeb* )
* Clone this git repository: *git@codebasehq.com:sysmo/consulting/mmofarm.git*
* Configure python interpreter to use the virtual enviorement (*/srv/VirtualEnv/SmoWebPlragform/bin/python*)

----------
Public key
----------

Login on the server (platform.sysmoltd.com)

* create .ssh folder (e.g. *sftp://platform.sysmoltd.com/home/milen/.ssh*)
* copy */home/milen/.ssh/id_rsa.pub* to *sftp://platform.sysmoltd.com/home/milen/.ssh*
* rename *id_rsa.pub* to *authorized_keys* in *sftp://platform.sysmoltd.com/home/milen/.ssh*

On the local computer:

* In terminal::

   sudo apt-get install openssh-server

-------------------------------------
Installing packages on local computer
-------------------------------------

* In terminal::

   goVirtual
   fab installAptPackages

* Build external modules

 * Eclipse: in */SmoWeb/smo/media/CoolProp/setup.py* set ``coolPropSrcFolder`` to the coolprop source folder and ``LDFLAGS`` to the folder with coolprop static library
 * In terminal::
 
      fab buildExtModules

-----------------------------
Running the develpment server
-----------------------------

In terminal (every time):: 

   goVirtual
   cdSmoWeb
   python manage.py runserver 
   
(or run **manage.py** from Eclipse with input parameters *runserver*)

In firefox (http://127.0.0.1:8000/ThermoFluids/HeatExchange1D)

   

