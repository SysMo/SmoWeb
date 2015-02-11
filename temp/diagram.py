import numpy as np
import matplotlib.pyplot as plt
from smo.media.CoolProp.CoolProp import FluidState, Fluid

fluidName = "CarbonDioxide" 
fState = FluidState(fluidName)

f = Fluid(fluidName)
# f.critical['p']

s_Arr = np.arange(900, 2200, 10)
p_Arr = np.arange(40 * 1e5, 120 * 1e5, 10 * 1e5)

fig = plt.figure()
ax1 = plt.gca()

for p in p_Arr:
    T_Arr = np.zeros((len(s_Arr),))
#     vQ_Arr = np.zeros((len(s_Arr),))
    for i in range(len(s_Arr)):
        fState.update('S', s_Arr[i], 'P', p)
        T_Arr[i] = fState.T - 273.15
#         if fState.isTwoPhase():
#             fState.update_Tq('S', s_Arr[i], 'Q', p)
        
    ax1.plot(s_Arr, T_Arr, label = "p=" + str(p/1e5) + " bar", color = 'b')

ax1.set_ylim([0, 100])
plt.title(fluidName)
plt.xlabel('S [J/kgK]')
plt.ylabel('T [C]')
plt.legend()
plt.show()
        
    
    
