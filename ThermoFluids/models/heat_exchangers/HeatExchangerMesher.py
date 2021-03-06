'''
Created on Apr 9, 2015

@author:  Milen Borisow
@copyright: SysMo Ltd, Bulgaria
'''
import fipy as FP
import numpy as np
import smo.math.util as sm

from smo.util import AttributeDict 
from cStringIO import StringIO
        
class HeatExchangerMesher():    
    def __init__(self):
        self.mesh = None
        
    def addPoint2D(self, x, y, cellSize):
        sMesh = self.sMesh
        
        sMesh.write("Point({0}) = {{ {1}, {2}, 0, {3} }};\n".format(
            self.pointId, x, y, cellSize))
        self.pointId += 1
        
    def addCircle2D(self, radius, cellSize, radialPosition = 0, angularPosition = 0, name = None):
        sMesh = self.sMesh
        
        (xc, yc) = sm.pol2cart(radialPosition, angularPosition) # get (x,y) coordinates of the center of the circle
        
        centerPointId = self.pointId
        self.addPoint2D(xc, yc, cellSize)
        pointId1 = self.pointId
        self.addPoint2D(xc - radius, yc, cellSize)
        pointId2 = self.pointId
        self.addPoint2D(xc, yc + radius, cellSize)
        pointId3 = self.pointId
        self.addPoint2D(xc + radius, yc, cellSize)
        pointId4 = self.pointId
        self.addPoint2D(xc, yc - radius, cellSize)
        
        circleArcId1 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId1, centerPointId, pointId2))
        self.circleArcId += 1
        
        circleArcId2 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId2, centerPointId, pointId3))
        self.circleArcId += 1
        
        circleArcId3 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId3, centerPointId, pointId4))
        self.circleArcId += 1
        
        circleArcId4 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId4, centerPointId, pointId1))
        self.circleArcId += 1
        
        sMesh.write("Line Loop({0}) = {{{1}, {2}, {3}, {4}}};\n".format(
            self.circleId, circleArcId1, circleArcId2, circleArcId3, circleArcId4))
        self.circleId += 1
        
        if name:
            sMesh.write('Physical Line("{0}") = {{ {1}, {2}, {3}, {4} }};\n'.format(
                name, circleArcId1, circleArcId2, circleArcId3, circleArcId4))

    def addChannelGroup(self, channelGroup = None, **kwargs): 
        if channelGroup == None:
            channelGroup = AttributeDict(kwargs)

        if (channelGroup.number <= 0):
            return
        
        offsetAngle = 2 * np.pi / channelGroup.number
        for i in range(int(channelGroup.number)):
            self.addCircle2D(
                 radius = channelGroup.externalDiameter / 2.,
                 cellSize = channelGroup.cellSize,
                 radialPosition = channelGroup.radialPosition, 
                 angularPosition = channelGroup.startingAngle + i * offsetAngle,
                 name = "{0}_{1}".format(channelGroup.channelName, i+1),
            )
    
    def addSurface(self, beginId, endId, name):
        sMesh = self.sMesh
        
        circleIds = ', '.join(str(x) for x in range(beginId, endId))
        sMesh.write("Plane Surface({0}) = {{ {1} }};\n".format(
            self.planeSurfaceId, circleIds))
        
        if name:
            sMesh.write('Physical Surface("{0}") = {{ {1} }};\n'.format(
                name, self.planeSurfaceId))
        
        self.planeSurfaceId += 1

    def create(self, heatExch = None, **kwargs): 
        if heatExch == None:
            heatExch = AttributeDict(kwargs)

        #===== Create the gmsh script =====#      
        # Geometry object IDs
        self.pointId = 1
        self.circleArcId = 1
        self.circleId = 1 #loop line
        self.planeSurfaceId = 1

        # Initialize gmsh script
        self.sMesh = StringIO()
        
        # Add the outer block circle
        self.addCircle2D(
            radius = heatExch.blockGeom.diameter / 2.0, 
            cellSize = heatExch.externalChannelGeom.cellSize, 
            radialPosition = 0, 
            angularPosition = 0,
            name = "OuterBoundary"
        )
        
        # Add the Primary channels
        self.addChannelGroup(heatExch.primaryChannelsGeom)
        self.addChannelGroup(heatExch.secondaryChannelsGeom)

        # Add the cross section surface 
        self.addSurface(beginId = 1, endId = self.circleId, name = "CrossSection")
        
        # Get the gmsh script
        gmshScript = self.sMesh.getvalue()
        self.sMesh.close()
        #===== Generate the mesh =====#
        self.mesh = FP.Gmsh2D(gmshScript)
        
    def addCircle2D_gmsh(self, radius, cellSize, radialPosition = 0, angularPosition = 0, name = None):
        #:WARRANTY: sometimes this method doesn't work
        sMesh = self.sMesh
        
        centerPointId = self.pointId
        self.addPoint2D(0, 0, cellSize)
        pointId1 = self.pointId
        self.addPoint2D(-radius, 0, cellSize)
        pointId2 = self.pointId
        self.addPoint2D(0, radius, cellSize)
        pointId3 = self.pointId
        self.addPoint2D(radius, 0, cellSize)
        pointId4 = self.pointId
        self.addPoint2D(0, -radius, cellSize)
        
        if radialPosition != 0.0:
            sMesh.write("Translate {{ {0}, 0, 0 }} {{ Point{{ {1}, {2}, {3}, {4}, {5} }}; }}\n".format(
                radialPosition, centerPointId, pointId1, pointId2, pointId3, pointId4))
        if angularPosition != 0.0:
            sMesh.write("Rotate {{ {{0, 0, 1}}, {{0, 0, 0}}, {0} }} {{ Point{{ {1}, {2}, {3}, {4}, {5} }}; }}\n".format(
                angularPosition, centerPointId, pointId1, pointId2, pointId3, pointId4))
        
        circleArcId1 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId1, centerPointId, pointId2))
        self.circleArcId += 1
        
        circleArcId2 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId2, centerPointId, pointId3))
        self.circleArcId += 1
        
        circleArcId3 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId3, centerPointId, pointId4))
        self.circleArcId += 1
        
        circleArcId4 = self.circleArcId 
        sMesh.write("Circle({0}) = {{ {1}, {2}, {3} }};\n".format(
            self.circleArcId, pointId4, centerPointId, pointId1))
        self.circleArcId += 1
        
        sMesh.write("Line Loop({0}) = {{{1}, {2}, {3}, {4}}};\n".format(
            self.circleId, circleArcId1, circleArcId2, circleArcId3, circleArcId4))
        self.circleId += 1
        
        if name:
            sMesh.write('Physical Line("{0}") = {{ {1}, {2}, {3}, {4} }};\n'.format(
                name, circleArcId1, circleArcId2, circleArcId3, circleArcId4))
