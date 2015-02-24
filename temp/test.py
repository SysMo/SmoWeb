from smo.media.CoolProp.CoolProp import FluidState

class DerivativeTest:
    def __init__ (self, fluid):
        self.fluid = fluid
        self.fState = FluidState(self.fluid)

    def numerical_derivative(self, stateVarNum,
                                    stateVarDenom, stateVarDenom_val, 
                                    stateVarConst, stateVarConst_val):
        """
        stateVarNum - name of state variable in numerator of the derivative (name is in style of FluidState properties)
        stateVarDenom - name of state variable in denominator of the derivative (name is in style of FluidState.update arguments)
        stateVarConst - name of constant state variable (name is in style of FluidState.update arguments)
        """
        self.fState.update(stateVarDenom, stateVarDenom_val, stateVarConst, stateVarConst_val)
        stateVarNum_val = getattr(self.fState, stateVarNum)
        stateVarDenom_val_new = stateVarDenom_val * 1.000001
        self.fState.update(stateVarDenom, stateVarDenom_val_new, stateVarConst, stateVarConst_val)
        stateVarNum_val_new = getattr(self.fState, stateVarNum)
        num_derivative = (stateVarNum_val_new - stateVarNum_val) / (stateVarDenom_val_new - stateVarDenom_val)
        return num_derivative
    
    @staticmethod
    def test():
        test_instance = DerivativeTest("Water")
        _drhodT_s = test_instance.numerical_derivative('rho', 
                                                     'T', 633.15,
                                                     'S', 4000)
        print ('Numerical: ' + str(_drhodT_s))
        fState = FluidState("Water")
        fState.update_Ts(633.15, 4000)
        print ('Analytical: ' + str(fState.rho**2 * fState.dsdT_v / fState.dpdT_v))
        print ('q = {}'.format(fState.q))

if __name__ == '__main__':
    DerivativeTest.test()