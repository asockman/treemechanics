'''

Cases:
self.inc                                       | self.rel | parent.inc | self.o
-----------------------------------------------+----------+------------+-------
parent.inc += self.rel                         | 0        | all        | all
parent.inc + self.rel                          | all      | 0          | all
parent.inc - self.rel                          | all      | all        | 0
parent.inc + self.rel                          | all      | all        | pi
self.rel*cos(parent.inc)                       | all      | all        | pi/2, 3pi/2
parent.inc - self.rel*cos(self.o)              | all      | right      | all
parent.inc - self.rel                          | all      | pi         | all
                                               |          |            |


'''
import numpy as np

class Branchoid(object):
    def __init__(self, p):
        self.relinc = 0
        self.o = 0

        self.parent = p
        self.parent.children.append(self)
        self.children = []

        self.inc, self.az = self.get_global_frame()

        #self.relorigin = 5
        self.pos = self.parent.get_end(5)

    def get_global_frame(self):
        phi = self.parent.az
        tht = self.parent.inc
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

    def get_end(self, length):
        return self.pos + self.get_vector()*length

    def get_vector(self):
        x = np.cos(self.az)*np.sin(self.inc)
        y = np.cos(self.inc)
        z = np.sin(self.az)*np.sin(self.inc)
        return np.array([x, y, z])

class Seedoid(Branchoid):
    def __init__(self):
        self.pos = np.array([0, 0, 0])
        self.az = 0
        self.inc = 0
        self.children = []

    def get_end(self, length):
        return self.pos

if __name__ == "__main__":

    import visual as v

    class VBranchoid(Branchoid):
        def __init__(self, *a):
            super().__init__(*a)
            self.cone = v.cone(pos=self.pos, axis=(self.get_end(10)-self.pos))
            self.trail = v.points(pos=[(0, 0, 0)])

        def draw(self):
            self.cone.pos = self.pos
            self.cone.axis = (self.get_end(10)-self.pos)
            self.cone.color = (((1-(np.cos(self.o)))/2), 0, ((1+(np.cos(self.o)))/2))

            self.trail.pos = list(self.trail.pos) + [self.get_end(10)]
            self.trail.color = list(self.trail.color) + [self.cone.color]
            if self.children:
                for b in self.children:
                    if type(b) == type(self):
                        b.draw()

    display = v.display(title="my own tree-thing!",width=1000,height=800)
    seed = Seedoid()
    p = VBranchoid(seed)
    p.relinc = np.pi/2
    p.o = np.pi/3
    c = VBranchoid(p)
    c.relinc = 0
    gc = VBranchoid(c)
    #gc.relinc = np.pi/4
    sineit = 0
    qrqrq = 0
    sinedog = 0
    while 1:
        if display.kb.keys:
            key = display.kb.getkey()
            if key == 'e': sineit = 1
            else: sineit = 0
            if key == 'r': qrqrq = 1
            else: qrqrq = 0


        if sineit:
            sinedog += 0.1
            p.o = sinedog/4
            #p.relinc = sinedog
            #c.o = sinedog
            p.relinc = np.pi/4+np.sin(sinedog*2)*(np.pi/8)
            #c.o = -sinedog/10
            c.inc, c.az = c.get_global_frame()
            p.inc, p.az = p.get_global_frame()
            gc.inc, gc.az = gc.get_global_frame()
            #c.inc = gc.inc
            #c.az = gc.az
            c.pos = p.get_end(5)
            gc.pos = c.get_end(5)
        #if qrqrq:

        p.draw()
