import matplotlib.pylab as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import math

class HeatExchangerCrossSectionProfile():
    def __init__(self, originX = 0, originY = 0):
        self.originX = originX
        self.originY = originY
        self.channelPatches = []
        self.dimensionLines = []
        self.dimensionLabels = []
        self.dimensionLabelAngles = []
    
    def addDimension(self, line, label, labelAngle):
        self.dimensionLines.append(line)
        self.dimensionLabels.append(label)
        self.dimensionLabelAngles.append(labelAngle)
    
    def addBlock(self, blockGeom):
        self.blockRadius = blockGeom.diameter / 2.
        self.blockPatch = Circle((self.originX, self.originY), self.blockRadius)
        self.addDimension([[self.originX - self.blockRadius, self.originX + self.blockRadius], [self.originY - 1.1 * self.blockRadius, self.originY - 1.1 * self.blockRadius]],
                          self.blockRadius * 2, 0)
    
    def addChannels(self, channelsGeom):
        for i in range(channelsGeom.number):
            angle = 360. / channelsGeom.number * i + math.degrees(channelsGeom.startingAngle)
            channelCenterX = self.originX + \
                channelsGeom.radialPosition * math.cos(math.radians(angle))
            channelCenterY = self.originY + \
                channelsGeom.radialPosition * math.sin(math.radians(angle))
            channelRadius = channelsGeom.externalDiameter / 2.
            self.channelPatches.append(Circle((channelCenterX, channelCenterY), channelRadius))
            if (i == 0):
                self.addDimension([[self.originX, channelCenterX], [self.originY, channelCenterY]],
                                  channelsGeom.radialPosition, angle)
                self.addDimension([[channelCenterX + channelRadius * math.cos(math.radians(angle + 90)), channelCenterX + channelRadius * math.cos(math.radians(angle - 90))], [channelCenterY + channelRadius * math.sin(math.radians(angle + 90)) , channelCenterY + channelRadius * math.sin(math.radians(angle - 90))]],
                                  channelsGeom.externalDiameter, angle-90)
    
    def plotGeometry(self, ax = None):
        if (ax is None):
            fig = plt.figure()
            ax = fig.add_subplot(111)
        ax.set_aspect(1)
        
        self.blockPatch.set_facecolor('#F0F0F0')
        self.blockPatch.set_edgecolor('k')
        ax.add_patch(self.blockPatch)    
        
        pc = PatchCollection(self.channelPatches, match_original = True)
        pc.set_facecolor('w')
        pc.set_edgecolor('k')
        pc.set_zorder(2)
        ax.add_collection(pc)
           
        self.plotDimensions(ax)
        ax.set_xlim(-1.05 * self.blockRadius, 1.05 * self.blockRadius)
        ax.set_ylim(-1.15 * self.blockRadius, 1.05 * self.blockRadius)
        plt.show()
    
    
    def plotDimensions(self, ax):            
        for i in range(len(self.dimensionLines)):
            x1, x2 = self.dimensionLines[i][0]
            y1, y2 = self.dimensionLines[i][1]
            ax.plot([x1, x2], [y1, y2], 'r', zorder=3)
            ax.annotate('', xy = (x1, y1), xycoords='data',
                        xytext=(x2, y2), textcoords='data',
                        arrowprops={'arrowstyle': '<->', 'color': 'r'})
            if (x1 == x2):
                xLabel = x1
                yLabel = y1 + (y2 - y1) / 2.
            else:
                a = (y2 - y1) / (x2 - x1)      
                b = y1 - a * x1
                xLabel = x1 + (x2 - x1) / 2.
                yLabel = a * xLabel + b
            ax.annotate("{0}".format(self.dimensionLabels[i] * 1e3), 
                                    xy = (xLabel, yLabel),
                                    xytext=(2, 2),
                                    textcoords='offset points',
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
        