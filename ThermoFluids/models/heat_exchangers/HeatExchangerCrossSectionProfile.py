import matplotlib.pylab as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import math

class HeatExchangerCrossSectionProfile():
    def __init__(self, originX = 0, originY = 0):
        self.originX = originX
        self.originY = originY
        self.patches = []
        self.dimensionLines = []
        self.dimensionLabels = []
        self.dimensionLabelAngles = []
    
    def addBlock(self, blockGeom):
        self.blockRadius = blockGeom.diameter / 2.
        self.patches.append(Circle((self.originX, self.originY), self.blockRadius))
        self.dimensionLines.append([[self.originX, self.originX-self.blockRadius], [self.originY, self.originY]])
        self.dimensionLabels.append(self.blockRadius)
        self.dimensionLabelAngles.append(0)
    
    def addChannels(self, channelsGeom):
        for i in range(channelsGeom.number):
            angle = 360. / channelsGeom.number * i + math.degrees(channelsGeom.startingAngle)
            channelCenterX = self.originX + \
                channelsGeom.radialPosition * math.cos(math.radians(angle))
            channelCenterY = self.originY + \
                channelsGeom.radialPosition * math.sin(math.radians(angle))
            channelRadius = channelsGeom.externalDiameter / 2.
            self.patches.append(Circle((channelCenterX, channelCenterY), channelRadius))
            if (i == 0):
                self.dimensionLines.append([[self.originX, channelCenterX], [self.originY, channelCenterY]])
                self.dimensionLabels.append(channelsGeom.radialPosition)
                self.dimensionLabelAngles.append(angle)
                self.dimensionLines.append([[channelCenterX + channelRadius * math.cos(math.radians(angle + 90)), channelCenterX + channelRadius * math.cos(math.radians(angle - 90))], 
                                            [channelCenterY + channelRadius * math.sin(math.radians(angle + 90)) , channelCenterY + channelRadius * math.sin(math.radians(angle - 90))]])
                self.dimensionLabels.append(channelsGeom.externalDiameter)
                self.dimensionLabelAngles.append(angle-90)
    
    def plotGeometry(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        ax.set_aspect(1)   
        pc = PatchCollection(self.patches, match_original = True, autolim = True)
        pc.set_facecolor('w')
        pc.set_edgecolor('k')
        ax.add_collection(pc)     
        self.plotDimensions(ax)
        ax.set_xlim(-1.1 * self.blockRadius, 1.1 * self.blockRadius)
        ax.set_ylim(-1.1 * self.blockRadius, 1.1 * self.blockRadius)
        plt.show()
    
    def plotDimensions(self, ax):
        for i in range(len(self.dimensionLines)):
            plt.plot(self.dimensionLines[i][0], self.dimensionLines[i][1])
            ax.annotate("{0}".format(self.dimensionLabels[i] * 1e3), 
                                    xy = (self.dimensionLines[i][0][1], self.dimensionLines[i][1][1]),
                                    rotation = self.dimensionLabelAngles[i])
        
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
        