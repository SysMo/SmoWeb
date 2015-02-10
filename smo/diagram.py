import numpy as np
import matplotlib.pyplot as plt
from smo.media.CoolProp.CoolProp import FluidState

fluidName = "ParaHydrogen" 
fState = FluidState(fluidName)
fState.update('P', 80*1e5, 'D', 1)
fState = FluidState(fluidName)

s_Arr = np.arange(1e3, 8e4, 1e3)
p_Arr = np.arange(1e5, 80 * 1e5, 10 * 1e5)

# fig = plt.figure()
# ax = plt.gca()

for p in p_Arr:
    T_Arr = np.zeros((len(s_Arr),))
    for i in range(len(s_Arr)):
        fState.update('S', s_Arr[i], 'P', p)
        T_Arr[i] = fState.T
    plt.plot(s_Arr, T_Arr, label="p=" + str(p/1e5) + ' bar')

plt.title(fluidName)
plt.xlabel('S [kJ/kgK]')
plt.ylabel('T [K]')
plt.legend()
plt.show()
        
    
    
