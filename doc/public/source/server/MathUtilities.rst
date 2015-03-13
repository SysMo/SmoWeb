==============
Math utilities
==============
.. module:: smo.math.util

The module provides the following classes and functions:

.. autofunction:: formatNumber

.. autoclass:: Interpolator1D

.. autoclass:: SectionCalculator

.. autoclass:: NamedStateVector

Example usage::

   >>> a = NamedStateVector(['T', 'p', 'h'])
   >>> n1 = np.array([3, 7, 4])
   >>> a.set(n1)
   >>> print('T = {}, p = {}, h = {}'.format(a.T, a.p, a.h))
   T = 3, p = 7, h = 4
   >>> a.T = 56
   >>> a.h = -20
   >>> print('T = {}, p = {}, h = {}'.format(a.T, a.p, a.h))
   T = 56, p = 7, h = -20
   >>> print (a.get())
   [ 56   7 -20]
   