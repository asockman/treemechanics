""" trees v0.2
procedurally generated foliage
(implicitly happy)

agrippa kellum : june 2013
"""

__all__ = ['Branch', 'Seed']

import numpy as np
import copy
np.random.seed(7)
seglength = 1
C = 600
k = 0.005
thresholdE = 10e-3
memoryrate = 0.001

class Branch(object):
    def __init__(self, inc, ori, pos, parent):
        self.parent = parent
        self.parentseg = parent.segs[-1]
        self.char = parent.char
        self.segs = [self.Segment(0, 0, 0, self)]

        self.length = 0
        self.radius = 1/100
        self.children = []
        self.growtick = 0
        self.order = parent.order + 1

        self.relinc = inc
        self.o = ori
        self.inc, self.az = self.get_global_frame()
        #self.inc = self.parentseg.inc + self.relinc
        #self.az = self.parent.az + self.o

        self.pos = np.array(pos)
        self.relativepos = (np.sum((self.pos-parent.pos)**2))**0.5
        self.end = np.array(pos)
        self.apex = 1

    def get_global_frame(self):
        if self.order <= 1: #SPECIAL CASE ALERT#-------------------------------
            return self.relinc, self.o
        phi = self.parent.az
        tht = self.parentseg.inc
        yrotation = np.array([[np.cos(phi), 0, -np.sin(phi)],
                              [0, 1, 0],
                              [np.sin(phi), 0, np.cos(phi)]])
        zrotation = np.array([[np.cos(tht), np.sin(tht), 0],
                              [-np.sin(tht), np.cos(tht), 0],
                              [0, 0, 1]])
        relvect = self.get_rel_vector()
        rotation = np.dot(yrotation, zrotation)
        globvect = np.dot(rotation, relvect)
        globtht = np.arccos(globvect[1])
        #phi = arctan of z/x
        globphi = np.arctan2(globvect[2],globvect[0])
        return globtht, globphi

    def get_rel_vector(self):
        x = np.cos(self.o)*np.sin(self.relinc)
        y = np.cos(self.relinc)
        z = np.sin(self.o)*np.sin(self.relinc)
        return np.array([x, y, z])

    class Segment(object):
        def __init__(self, length, incr_unlo, incr_lo, branch, radius = 0,
                     inc='uk', F='uk', M='uk', pos='uk', end='uk'):
            self.branch = branch
            self.incr_unlo = incr_unlo
            self.incr_lo = incr_lo
            self.length = length
            self.radius = radius

            self.children = set() #!NOT IMPLOMENTED
            self.inc = inc
            self.F = F
            self.M = M
            self.pos = pos
            self.end = end
            self.density = 4

        def get_end(self, length):
            return self.pos + self.get_vector()*length

        def get_vector(self):
            x = np.cos(self.branch.az)*np.sin(self.inc)
            y = np.cos(self.inc)
            z = np.sin(self.branch.az)*np.sin(self.inc)
            return np.array([x, y, z])

        def volume(self, r):
            V =(np.pi*self.length/3)*(self.radius**2 + self.radius*r + r**2)
            return V

    def get_point(self, length):
        for seg in self.segs:
            if seg.length < length:
                length -= seg.length
            else: break
        return seg.get_end(length)

    def delete(self):
        while self.children:
            self.children[0].delete()

        self.parent.children.remove(self)
        del self

    def branchoff(self):
        azmod = np.random.random() * self.char['azrange']
        incmod = np.random.random() * self.char['incrange']
        self.children.append(self.__class__(np.pi/8, azmod, self.end, self)) #DEBUG ALERT

    def resolve(self):
        ''' Resolve segment inclination rates considering new load.
        Based upon Catherine Jirasek's algorithm
        '''
        while True:
            oldsegs = copy.copy(self.segs)
            # Step 1
            nextinc = self.inc
            for seg in self.segs:
                seg.inc = nextinc
                nextinc += seg.incr_lo*seg.length

            # Step 2
            prevF = self.char['gravitropism'] #placeholder gravitropism
            prevM = 0
            prevr = 0
            for seg in reversed(self.segs):
                seg.F = prevF
                seg.M = prevM
                #volume based weight that is wonky atm
                #prevF += seg.volume(prevr)*seg.density
                prevF += seg.density*seg.length
                #sin because everything is rotated i dont know how i rotated everything what
                prevM += np.sin(seg.inc)*seg.F*seg.length
                prevr = seg.radius

            # Step 3
            maxE = 0
            for seg in self.segs:
                seg.E = seg.M + C*seg.radius*seg.length*(seg.incr_unlo-seg.incr_lo)
                if abs(seg.E) > maxE: maxE = abs(seg.E)

            # Step 4
            if maxE > thresholdE:
                for seg, oldseg in zip(self.segs, oldsegs):
                    oldseg.incr_lo += k*seg.E
                    self.segs = oldsegs
            else:
                nextpos = self.pos
                for seg in self.segs:
                    seg.pos = nextpos
                    nextpos = seg.get_end(seg.length)
                self.end = nextpos
                break

    def grow(self):
        self.inc, self.az = self.get_global_frame()
        self.pos = self.parent.get_point(self.relativepos)
        self.resolve()

        self.growtick += self.char['dominance']**self.order
        if self.growtick >= 1: #if i have received enough nutrients to grow...
            self.growtick %= 1
            self.radius += self.char['thicken']
            for seg in self.segs:
                seg.radius += self.char['thicken']
            if self.apex: #...and i have a meristem...
                if np.random.random() <= self.char['splitchance']:
                    self.branchoff()
                self.length += self.char['growth']
                self.segs[-1].length += self.char['growth']
                if self.segs[-1].length > seglength:
                    excess = seglength - self.segs[-1].length
                    self.segs[-1].length = seglength
                    self.segs.append(self.Segment(excess, 0, 0, self))
                    self.resolve()

        for seg in self.segs:
            seg.incr_unlo -= (seg.incr_unlo-seg.incr_lo)*memoryrate

        for b in self.children:
            b.grow()


class Seed(Branch):
    ''' A shapeless Branch who has no parent -- used to start a tree

    Parameters
    ----------
    pos : array-like
        location of Seed

    char : dict
        dictionary of characteristics which determine branch behavior.
        children of the seed will inheirit.

    Example
    -------
    >>> Seed
    '''
    def __init__(self, pos, char):
        self.az = 0
        self.inc = 0
        self.order = -1
        self.pos = pos
        self.char = char
        self.segs = [self.Segment(0, 0, 0, self, inc=self.inc)]

    def get_point(self, length):
        return self.pos

if __name__ == "__main__":

    import visual as v

    class VBranch(Branch):
        def __init__(self, *a):
            super().__init__(*a)
            self.curve = v.extrusion(pos=[self.pos],
                                     shape=v.paths.circle(pos=(0,0), radius = 1),
                                     color=(0.6, 0.4, 0),
                                     scale=((0,0))
                                     )

        def delete(self):
            self.curve.visible = False
            super().delete()

        def draw(self):
            pos = [seg.pos for seg in self.segs]
            pos.append(self.end)
            scale = [(seg.radius, seg.radius) for seg in self.segs]
            scale.append((0.001, 0.001))
            self.curve.pos = pos
            self.curve.scale = scale
            self.curve.color = (((1-(np.cos(self.o)))/2), 0, ((1+(np.cos(self.o)))/2))

            if self.children:
                for b in self.children:
                    b.draw()

    height = 800
    width = 1000
    # random.seed(232)

    characteristics = { 'incrange' : 0.5, #unused
                        'azrange' : np.pi*2,
                        'growth' : 0.03,
                        'thicken' : 0.001,
                        'splitchance' : 0.01,
                        'maxinc' : np.pi/2,
                        'gravitropism' : -10,
                        'dominance' : 0.9  #how much nutrients does a parent give its child?
                        }

    display = v.display(title="my own tree!",width=width,height=height)
    seed = Seed((0, 0, 0), characteristics)
    tree = VBranch(0, 0, (0, 0, 0), seed)
    growit = 0

    while 1:
        if display.kb.keys:
            key = display.kb.getkey()
            if key == 'e':
                growit = 1
            else:
                growit = 0
            if key == 'r':
                spin = 1
            else: spin = 0

        if growit:
            tree.grow()
            display.center = tree.pos+(tree.end/2)
            tree.draw()
