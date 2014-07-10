""" trees v0.2
procedurally generated foliage
(implicitly happy)

agrippa kellum : june 2013
"""

__all__ = ['Branch', 'Trunk']

import sys, random, math, time, visual as v, numpy as np

class Branch(object):
    def __init__(self,inc,az,parent,origin):
        self.parent = parent

        self.size = 1
        self.children = []
        self.growtick = 0
        self.order = parent.order + 1
        self.splitchance = parent.splitchance
        
        self.thickness = 1/100
        self.thicken = 0.1/100
        
        self.incmod = inc
        self.inclination = parent.inclination+self.incmod
        self.azmod = az
        self.azimuth = parent.azimuth+self.azmod
        
        self.origin = np.array(origin)
        self.relativeorigin = (np.sum((self.origin-parent.origin)**2))**0.5
        self.end = np.array(origin)
        self.terminated = 0
        self.age = 0
    
    def delete(self):
        while self.children:
            self.children[0].delete()
        
        self.parent.children.remove(self)
        del self
    
    def get_end(self,size):
        x2 = self.origin[0] + (math.cos(self.azimuth) * math.sin(self.inclination) * size)
        y2 = self.origin[1] + (math.cos(self.inclination) * size)
        z2 = self.origin[2] + (math.sin(self.azimuth) * math.sin(self.inclination) * size)
        return np.array([x2,y2,z2])
    
    # @classmethod
    
    def branchoff(self):
        azmod = (random.random()*azrange*2)-azrange
        incmod = (random.random()*incrange*2)-incrange
        while abs(self.inclination+incmod) > maxinc:
            incmod = (random.random()*incrange*2)-incrange
        self.children.append(self.__class__(incmod, azmod, self, self.end))
    
    def grow(self):
        self.growtick += dominance**self.order
        if self.growtick >= 1: #if i have received enough nutrients to grow...
            self.growtick %= 1
            self.age += 1 #TEMPORARY
            self.thickness += self.thicken
            if self.terminated == 0: #...and i have a meristem...
                if random.random() <= self.splitchance:
                    self.branchoff()
                self.size += growth
        self.incmod *= branchdrop
        if abs(self.inclination) < maxinc:
            self.inclination = self.parent.inclination+self.incmod
        else:
            self.delete()
        self.origin = self.parent.get_end(self.relativeorigin)
        self.end = self.get_end(self.size)
            
        for b in self.children:
            b.grow()
   
class Trunk(Branch):
    ''' A Branch who has no parent -- used to start a tree '''
    def __init__(self, origin):
        self.azimuth = random.random()*math.pi*2
        self.inclination = 0
        self.order = -1
        self.splitchance = splitchance
        
        super().__init__(0, 0, self,origin)
        
class VBranch(Branch, v.cone):
    def __init__(self, *a):
        super().__init__(*a)
        v.cone.__init__(self, pos=self.origin, axis=(self.end-self.origin), radius=self.thickness, color=treebark)
        
    def delete(self):
        self.visible = False
        super().delete()
        
    def draw(self):
        self.pos = self.origin
        self.axis = (self.end-self.origin)
        self.radius = (self.thickness)
        
        if self.children:
            for b in self.children:
                b.draw()

class VTrunk(Trunk, VBranch):
    pass

height = 800
width = 1000
# random.seed(232)


green =    (0.2,0.8,0)
yello =    (0.8,0.8,0)
treebark = (0.6,0.4,0)

incrange = 0.5
azrange = math.pi*2
growth = 0.03
splitchance = 0.005


leafmod = 0.1
maxinc = math.pi/2
branchdrop = 1.0005
dominance = 1 #how much nutrients does a parent give its child?
    
display = v.display(title="my own tree!",width=width,height=height)    
tree = VTrunk((0,0,0))
mousedown = 0
growit = 0


while 1:
    if display.kb.keys:
        key = display.kb.getkey()
        if key == 'e':
            growit = 1
        else:
            growit = 0

    if growit:
        tree.grow()
        display.center = tree.get_end(tree.size/2)
    
    tree.draw()