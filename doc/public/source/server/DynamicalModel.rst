===============
Dynamical model
===============

------------------------
Defining dynamical model
------------------------

Let's define a 'source force': component which outputs a constant force 
(e.g. gravity) acting on some body::

   class ForceSource(DynamicalModel):
      f = F.RealVariable(causality = CS.Output, variability = VR.Constant, default = -9.8)
      x = F.RealVariable(causality = CS.Input)
      v = F.RealVariable(causality = CS.Input)
      p = F.Port([f, v, x])

Each variable has a type (in this case Real), a causality (input/output/local/parameter) and variability
(continuous/discrete/constant). Ports are groups of variables which facilitate interconnecting components.

Let's also define a body (e.g. a ball) which can fall down in gravity. The state of the ball 
is defined by its position and its velocity::

   class BoundMass(DynamicalModel):
      m = F.RealVariable(causality = CS.Parameter, variability = VR.Constant, default = 10.)
      f = F.RealVariable(causality = CS.Input, default = 10.)
      x = F.RealState(start = 0.1)
      v = F.RealState(start = 1.)
      p = F.Port([f, v, x])

Now let's define a mechanical system, comprising of a force source and a ball connected to each other::

   class MechSystem(DynamicalModel):
      fs = F.SubModel(ForceSource)
      mass = F.SubModel(BoundMass)
      
      def __init__(self):
         self.fs.meta.p.connect(self.mass.meta.p)


   
-------------
Model classes
-------------

.. module:: smo.dynamical_models.core.DynamicalModel

.. autoclass:: DynamicalModelMeta


.. autoclass:: DynamicalModel

-------------
Field classes
-------------

.. module:: smo.dynamical_models.core.Fields

.. autoclass:: Causality
   :undoc-members:

.. autoclass:: Variability
   :undoc-members:

.. autoclass:: ModelField 
   
.. autoclass:: Function

.. autoclass:: Port

.. autoclass:: ScalarVariable

.. autoclass:: RealVariable

.. autoclass:: RealVariable

.. autoclass:: RealState

.. autoclass:: SubModel

----------------
Instance classes
----------------

.. autoclass:: InstanceField

.. autoclass:: InstanceVariable

.. autoclass:: InstanceFunction

.. autoclass:: InstancePort

.. autoclass:: DerivativeVector

------------------
Simulation actions
------------------

.. module:: smo.dynamical_models.core.SimulationActions

.. autoclass:: SimulationAction

.. autoclass:: SetRealState

.. autoclass:: GetRealStateDerivative

.. autoclass:: CallMethod

.. autoclass:: AssignValue

