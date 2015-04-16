import numpy as np
import matplotlib.pyplot as plt
import smo.media.CoolProp5 as CP5

csvFileName = 'Glysantin-Wasser+50-50.csv'
csvFluidLabel = 'CSV: Glysantin-Wasser-50%'

cpFluidMassFractions = 0.5
cpFluidName = 'MEG'
cpFluidLabel = 'CoolProp5: {0}-{1}%'.format(cpFluidName, cpFluidMassFractions*100)


def testCompareFluids_CsvVsCoolProp():
    # Read csv fluid data
    csvFluidData = np.genfromtxt(csvFileName, delimiter=',', names = True, skip_footer = 4)
    
    # Read CoolProp5 fluid data
    cpFluid = CP5.FluidStateFactory.createIncompressibleSolution(
        cpFluidName, cpFluidMassFractions)
    cpFluidData = csvFluidData.copy()
    
    for i in range(len(cpFluidData['T'])):
        p = 1e5 # [Pa]
        T = cpFluidData['T'][i]
        cpFluid.update_Tp(T,p)
        cpFluidData['rho'][i] = cpFluid.rho
        cpFluidData['cp'][i] = cpFluid.cp / 1e3
        cpFluidData['lambda'][i] = cpFluid.cond  
        cpFluidData['nu'][i] = 1e6 * cpFluid.mu / cpFluid.rho  
            
    # Plot 
    fig = plt.figure()
    
    ax1 = fig.add_subplot(221)
    plotFluidsProperty(ax1, 'Density', 'rho [kg/m**3]', 
        csvFluidData['T'], csvFluidData['rho'], 
        cpFluidData['T'], cpFluidData['rho'])
    
    ax2 = fig.add_subplot(222)
    plotFluidsProperty(ax2, 'Cp', 'cp [kJ/kg-K]', 
        csvFluidData['T'], csvFluidData['cp'], 
        cpFluidData['T'], cpFluidData['cp'])
    
    ax3 = fig.add_subplot(223)
    plotFluidsProperty(ax3, 'Thermal conductivity', 'lambda [W/K-m]', 
        csvFluidData['T'], csvFluidData['lambda'], 
        cpFluidData['T'], cpFluidData['lambda'])
    
    ax4 = fig.add_subplot(224)
    plotFluidsProperty(ax4, ' Kinetic viscosity', 'nu [mm**2/s]', 
        csvFluidData['T'], csvFluidData['nu'], 
        cpFluidData['T'], cpFluidData['nu'])
    
    plt.show()  
    
def plotFluidsProperty(ax, title, yLabel, x1Data, y1Data, x2Data, y2Data):
    err = np.abs(np.mean(100*(y1Data-y2Data)/y2Data))
    ax.set_title('{0} - mean error = {1:.2f}%'.format(title, err))    
    ax.set_xlabel('T [K]')
    ax.set_ylabel(yLabel)
    ax.plot(x1Data, y1Data, color = 'r', label = csvFluidLabel)
    ax.plot(x2Data, y2Data, color = 'b', label = cpFluidLabel)
    ax.legend()


if __name__ == "__main__":
    #testCoolProp5()
    testCompareFluids_CsvVsCoolProp()