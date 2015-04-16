import matplotlib.pylab as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import math

class HeatExchangerCrossSectionProfile():
    def __init__(self, originX = 0, originY = 0):
        self.patches = []
        self.originX = originX
        self.originY = originY
    
    def addBlock(self, blockGeom):
        self.blockRadius = blockGeom.diameter / 2.
        self.patches.append(Circle((self.originX, self.originY), self.blockRadius))
    
    def addChannels(self, channelsGeom):
        for i in range(channelsGeom.number):
            angle = 360. / channelsGeom.number * i + math.degrees(channelsGeom.startingAngle)
            channelCenterX = self.originX + \
                channelsGeom.radialPosition * math.cos(math.radians(angle))
            channelCenterY = self.originY + \
                channelsGeom.radialPosition * math.sin(math.radians(angle))
            channelRadius = channelsGeom.externalDiameter / 2.
            self.patches.append(Circle((channelCenterX, channelCenterY), channelRadius))
    
    def plotGeometry(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        ax.set_aspect(1)
        pc = PatchCollection(self.patches, match_original = True, autolim = True)
        pc.set_facecolor('w')
        pc.set_edgecolor('k')
        ax.add_collection(pc)
        ax.set_xlim(-1.1 * self.blockRadius, 1.1 * self.blockRadius)
        ax.set_ylim(-1.1 * self.blockRadius, 1.1 * self.blockRadius)
        
        plt.show()
        
    @staticmethod
    def test():
        from ThermoFluids.models.HeatExchangerDesign import CylindricalBlockHeatExchanger
        heatExchanger = CylindricalBlockHeatExchanger()
        crossSectionProfile = HeatExchangerCrossSectionProfile()
        crossSectionProfile.addBlock(heatExchanger.blockGeom)
        crossSectionProfile.addChannels(heatExchanger.primaryChannelsGeom)
        crossSectionProfile.addChannels(heatExchanger.secondaryChannelsGeom)
        crossSectionProfile.plotGeometry()
        
if __name__ == "__main__":
    HeatExchangerCrossSectionProfile.test()
        