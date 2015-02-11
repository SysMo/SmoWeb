import numpy as np
import matplotlib.pyplot as plt
from smo.media.CoolProp.CoolProp import FluidState, Fluid

fluidName = "CarbonDioxide" 
fState = FluidState(fluidName)

trippCoeff = 1.2

f = Fluid(fluidName)
fState.update_Tq(f.tripple['T'] * trippCoeff, 0)
dome_start = fState.s
fState.update_Tq(f.tripple['T'] * trippCoeff, 1)
dome_end = fState.s
dome_len = dome_end - dome_start
x_start = dome_start - dome_len / 4.
x_end = dome_end + dome_len * 3 / 4.

y_start = f.tripple['T'] * trippCoeff - 273.15
y_mid = f.critical['T'] - 273.15
y_end = y_start + 2 * (y_mid - y_start)


s_Arr = np.arange(x_start, x_end, (x_end - x_start)/ 200)
p_Arr = np.arange(f.tripple['p'] * trippCoeff, 2 * f.critical['p'], 
                  (2 * f.critical['p'] - f.tripple['p'] * trippCoeff)/20)

# s_Arr = np.arange(900, 2200, 10)
# p_Arr = np.arange(20 * 1e5, 150 * 1e5, 10 * 1e5)
q_Arr = np.arange(0, 1.1, 0.1)



fig = plt.figure()
ax1 = plt.gca()

# Isobars
for p in p_Arr:
    T_Arr = np.zeros((len(s_Arr),))
    for i in range(len(s_Arr)):
        fState.update_ps(p, s_Arr[i])
        T_Arr[i] = fState.T
    ax1.plot(s_Arr, T_Arr - 273.15, label = "p=" + str(p/1e5) + " bar", color = 'b')
    

# Vapor quality iso-lines
for q in q_Arr:
    s_List = []
    T_List = []
    for i in range(len(T_Arr)):
        if (T_Arr[i] >= f.tripple['T'] and T_Arr[i] < f.critical['T']):
            T_List.append(T_Arr[i])
            fState.update_Tq(T_Arr[i], q)
            s_List.append(fState.s)
    T_List.append(f.critical['T'])
    fState.update_Tq(f.critical['T'], q)
    s_List.append(fState.s)
    ax1.plot(np.array(s_List), np.array(T_List) - 273.15, color='r')

# Isenthalps
# for h in h_Arr:
#     s_List = []
#     T_List = []
#     for i in range(len(s_Arr)):
#         try:
#             fState.update('H', h, 'S', s_Arr[i])
#             s_List.append(s_Arr[i]) 
#             T_List.append(fState.T)
#         except:
#             pass
#     ax1.plot(np.array(s_List), np.array(T_List) - 273.15, 'go', label = "h=" + str(p/1e3) + " kJ/kg")


# T_Arr = np.arange(260, 473, 5)
# S, T = np.meshgrid(s_Arr, T_Arr)
# h_Arr = np.zeros((len(T_Arr), len(s_Arr)))
# 
# for i in range(len(s_Arr)):
#     for j in range(len(T_Arr)):
#         fState.update('S', s_Arr[i], 'T', T_Arr[j])
#         h_Arr[j][i] = fState.h
# 
# contPlot = ax1.contour(S, T - 273.15, h_Arr, 50, colors='green')
# ax1.clabel(contPlot, inline_spacing=0, use_clabeltext=True, fontsize=10, fmt="%1.1e")

ax1.set_xlim([x_start, x_end])
ax1.set_ylim([y_start, y_end])
plt.title(fluidName)
plt.xlabel('S [J/kgK]')
plt.ylabel('T [C]')
# plt.legend()
plt.show()
        
    
    
