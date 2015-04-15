import smo.media.CoolProp5.CoolProp as CP5
import smo.media.CoolProp5._constants as cst 

f1 = CP5.AbstractState('INCOMP', 'MEG2')
f1.set_mass_fractions([0.5])
f1.update(cst.PT_INPUTS, 1e5, 275, )

print "rho = ", f1.rhomass()
print "cp = ", f1.cpmass()
print "nu = ", f1.viscosity() / f1.rhomass()
print "lambda = ", f1.conductivity()