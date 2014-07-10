""" trees v0.2
procedurally generated foliage
(implicitly happy)

agrippa kellum : june 2013
"""

__all__ = ['Branch', 'Seed']

import numpy as np
import copy
seglength = 1
C = 1000
k = 0.005
thresholdE = 10e-3


class Branch(object):
    def __init__(self, inc, az, origin, parent):
        self.parent = parent
        self.char = parent.char

        self.segs = [self.Segment(0, 0, 0, self)]

        self.length = 0
        self.thickness = 1/100
        self.children = []
        self.growtick = 0
        self.order = parent.order + 1

        self.incmod = inc
        self.inclination = parent.inclination + self.incmod
        self.azmod = az
        self.azimuth = parent.azimuth+self.azmod

        self.origin = np.array(origin)
        self.relativeorigin = (np.sum((self.origin-parent.origin)**2))**0.5
        self.end = np.array(origin)
        self.apex = 1

    class Segment(object):
        def __init__(self, length, incr_unlo, incr_lo, branch,
                     inclination='na', F='na', M='na', pos='na', end='na'):
            self.branch = branch
            self.incr_unlo = incr_unlo
            self.incr_lo = incr_lo
            self.length = length

            self.children = set() #!NOT IMPLOMENTED
            self.inclination = inclination
            self.F = F
            self.M = M
            self.pos = pos
            self.end = end
            self.weight = 2 #need to be replaced

        def get_end(self, length):
            x2 = self.pos[0] + (np.cos(self.branch.azimuth)*np.sin(self.inclination)*length)
            y2 = self.pos[1] + (np.cos(self.inclination)*length)
            z2 = self.pos[2] + (np.sin(self.branch.azimuth)*np.sin(self.inclination)*length)
            return np.array([x2,y2,z2])

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
        azmod = (np.random.random() * self.char['azrange']*2) - self.char['azrange']
        incmod = (np.random.random() * self.char['incrange']*2) - self.char['incrange']
        while abs(self.inclination + incmod) > self.char['maxinc']:
            incmod = (np.random.random() * self.char['incrange']*2) - self.char['incrange']
        self.children.append(self.__class__(incmod, azmod, self.end, self))

    def resolve(self):
        ''' Resolve segment inclination rates considering new load.
        Based upon Catherine Jirasek's algorithm
        '''
        while True:
            oldsegs = copy.copy(self.segs)
            # Step 1
            nextinc = self.inclination
            for seg in self.segs:
                seg.inclination = nextinc
                nextinc += seg.incr_lo*seg.length

            # Step 2
            prevF = 0
            prevM = 0
            for seg in reversed(self.segs):
                seg.F = prevF
                seg.M = prevM
                prevF += seg.weight
                prevM += np.sin(seg.inclination)*seg.F*seg.length #sin because everything is rotated i dont know how i rotated everything what

            # Step 3
            maxE = 0
            for seg in self.segs:
                seg.E = seg.M + C*self.thickness*(seg.incr_unlo-seg.incr_lo)
                if abs(seg.E) > maxE: maxE = abs(seg.E)

            # Step 4
            if maxE > thresholdE:
                for seg, oldseg in zip(self.segs, oldsegs):
                    oldseg.incr_lo += k*seg.E
                    self.segs = oldsegs
            else:
                nextpos = self.origin
                for seg in self.segs:
                    seg.pos = nextpos
                    nextpos = seg.get_end(seg.length)
                self.end = nextpos
                break

    def grow(self):
        self.growtick += self.char['dominance']**self.order
        if self.growtick >= 1: #if i have received enough nutrients to grow...
            self.growtick %= 1
            self.thickness += self.char['thicken']
            if self.apex: #...and i have a meristem...
                if np.random.random() <= self.char['splitchance']:
                    self.branchoff()
                #self.length += self.char['growth']
                self.segs[-1].length += self.char['growth']
                if self.segs[-1].length > seglength:
                    excess = seglength - self.segs[-1].length
                    self.segs[-1].length = seglength
                    self.segs.append(self.Segment(excess, 0, 0, self))

        #self.incmod *= self.char['branchdrop']
        #if abs(self.inclination) < self.parent.char['maxinc']:
        #    self.inclination = self.parent.inclination+self.incmod
        #else:
        #    self.delete()
        self.origin = self.parent.get_point(self.relativeorigin)
        self.resolve()

        for b in self.children:
            b.grow()


class Seed(Branch):
    ''' A shapeless Branch who has no parent -- used to start a tree

    Parameters
    ----------
    origin : array-like
        location of Seed

    char : dict
        dictionary of characteristics which determine branch behavior.
        children of the seed will inheirit.

    Example
    -------
    >>> Seed
    '''
    def __init__(self, origin, char):
        self.azimuth = np.random.random()*np.pi*2
        self.inclination = 0
        self.order = -1
        self.origin = origin
        self.char = char

    def get_point(self, length):
        return self.origin

if __name__ == "__main__":

    import visual as v

    class VBranch(Branch):
        def __init__(self, *a):
            super().__init__(*a)
            self.curve = v.curve(pos=[self.origin], axis=(self.end-self.origin),
                               radius=self.thickness, color=(0.6,0.4,0))

        def delete(self):
            self.curve.visible = False
            super().delete()

        def draw(self):
            pos = [seg.pos for seg in self.segs]
            pos.append(self.end)
            self.curve.pos = pos
            self.curve.radius = (self.thickness)

            if self.children:
                for b in self.children:
                    b.draw()

    height = 800
    width = 1000
    # random.seed(232)

    characteristics = { 'incrange' : 0.5,
                        'azrange' : np.pi*2,
                        'growth' : 0.03,
                        'thicken' : 0.1/100,
                        'splitchance' : 0.010,
                        'maxinc' : np.pi/2,
                        'branchdrop' : 1.0015,
                        'dominance' : 1 #how much nutrients does a parent give its child?
                        }

    display = v.display(title="my own tree!",width=width,height=height)
    seed = Seed((0, 0, 0), characteristics)
    tree = VBranch(0, 0, (0, 0, 0), seed)
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
            display.center = tree.origin+(tree.end/2)
            tree.draw()
