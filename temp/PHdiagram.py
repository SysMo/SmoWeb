import numpy as np
import matplotlib.pyplot as plt
from smo.media.CoolProp.CoolProp import FluidState, Fluid

fluidName = "Oxygen" 
fState = FluidState(fluidName)

# Calculating axes
f = Fluid(fluidName)
trippCoeff = 1.2
fState.update_pq(f.tripple['p'] * trippCoeff, 0)
# Vapor quality dome
dome_start = fState.h
fState.update_pq(f.tripple['p'] * trippCoeff, 1)
dome_end = fState.h
dome_len = dome_end - dome_start
# X axis
x_start = dome_start - dome_len / 4.
x_end = dome_end + dome_len * 3 / 4.
# Y axis
crit2Tripp = f.critical['p'] / f.tripple['p']
if (crit2Tripp > 100):
    y_start = f.critical['p'] / 100
else:
    y_start = f.tripple['p'] * trippCoeff

y_mid = f.critical['p']
y_end = y_start + 2 * (y_mid - y_start)

# Vapor quality range
q_Arr = np.arange(0, 1.1, 0.1)
# Pressure range
p_Arr = np.logspace(np.log10(y_start), np.log10(y_end), num = 200)

# Isotherm levels
# T_levels = np.linspace(f.tripple['T'] * trippCoeff, 3 * f.critical['T'], 
#                   num = 30)

# Isentrop levels
# fState.update_Trho(f.tripple['T'], f.tripple['rhoL']) 
# fState.update_ph(y_start, x_start)
# s_min = fState.s
# s_max = fState.update_ph(y_start, x_end)
# s_max = fState.s
# s_levels = np.linspace(f.critical['s'] / 50., 4 * f.critical['s'], 
#                   num = 20)
# s_levels = np.linspace(s_min, s_max, 
#                   num = 20)

fig = plt.figure()
ax1 = plt.gca()

# Drawing isotherms
# for T in T_levels:
    # Enthalpy
#     H_Arr = np.zeros((len(p_Arr),))
#     for i in range(len(p_Arr)):
#         fState.update_Tp(T, p_Arr[i])
#         H_Arr[i] = fState.h
#     ax1.plot(H_Arr, p_Arr, label = "T=" + str(T - 273.15) + " C", color = 'r')
    
#     h_List = []
#     p_List = []
#     while (h <= x_end):
#         h = fState.h
#         p = fState.p
#         print p,h
#         h_List.append(fState.h)
#         p_List.append(fState.p)
#         rho = fState.rho
#         rho += 1
#         fState.update_Trho(T, rho)
#     ax1.plot(np.array(h_List), np.array(p_List), label = "T=" + str(T - 273.15) + " C", color = 'r')


# Isotherms
p = y_end
for h in np.linspace(x_start, x_end, 20):
    p_var = p
    h_var = h
    h_List = []
    p_List = []
    try:
        fState.update_ph(p, h)
    except:
        continue
    T = fState.T
    if (T < f.fluidLimits['TMin']):
        continue
    while (p_var >= y_start):
        h_List.append(h_var)
        p_List.append(p_var)
        rho = fState.rho
        rho *= 0.999
        if (rho <= f.fluidLimits['rhoMax']):
            fState.update_Trho(T, rho)
            p_var = fState.p
            h_var = fState.h
        else:
            break
    ax1.plot(np.array(h_List), np.array(p_List), 'r', label = "T=" + str(T - 273.15) + " C")

# Isohores
fState.update_Tp(f.tripple['T'] * trippCoeff, f.tripple['p'] * trippCoeff)
h_start = fState.h
for h in np.linspace(h_start, 10 * x_end, 20):
    p_var = p
    h_var = h
    h_List = []
    p_List = []
    try:
        fState.update_ph(p, h)
    except:
        continue 
    rho = fState.rho
    if (rho > f.fluidLimits['rhoMax']):
        continue
    while (p_var >= y_start):
        h_List.append(h_var)
        p_List.append(p_var)
        T = fState.T
        T *= 0.999
        if (f.fluidLimits['TMin'] <= T):
            fState.update_Trho(T, rho)
            p_var = fState.p
            h_var = fState.h
        else:
            print h
            break
    ax1.plot(np.array(h_List), np.array(p_List), 'g', label = "T=" + str(T - 273.15) + " C")
    
# Drawing isentrops
# for s in s_levels:
#     # Enthalpy
#     H_Arr = np.zeros((len(p_Arr),))
#     for i in range(len(p_Arr)):
#         fState.update_ps(p_Arr[i], s)
#         H_Arr[i] = fState.h
#     ax1.semilogy(H_Arr, p_Arr, label = "s=" + str(s) + " J/kgK", color = 'm')

# Vapor quality iso-lines
for q in q_Arr:
    h_List = []
    p_List = []
    for i in range(len(p_Arr)):
        if (p_Arr[i] >= f.tripple['p'] and p_Arr[i] < f.critical['p']):
            p_List.append(p_Arr[i])
            fState.update_pq(p_Arr[i], q)
            h_List.append(fState.h)
    p_List.append(f.critical['p'])
    fState.update_pq(f.critical['p'], q)
    h_List.append(fState.h)
    ax1.semilogy(np.array(h_List), np.array(p_List), color = 'black')

ax1.set_xlim([x_start, x_end])
ax1.set_ylim([y_start, y_end])
ax1.set_xscale('log')
plt.title(fluidName)
plt.xlabel('H [J/kgK]')
plt.ylabel('P [Pa]')
# plt.legend()
plt.show()