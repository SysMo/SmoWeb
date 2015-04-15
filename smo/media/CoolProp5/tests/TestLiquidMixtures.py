from smo.media.CoolProp5.CoolProp import AbstractState
import smo.media.CoolProp5._constants as cst 

#f1 = AbstractState('?', 'ParaHydrogen')
f1 = AbstractState('INCOMP', 'MEG')
f1.set_mass_fractions([0.5])
f1.update(cst.PT_INPUTS, 1e5, 273, )
print f1.rhomass()