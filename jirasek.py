import numpy as np
import pygame as pyg
import copy


'''
input:
    H : Heading vector
    seglengs : segment lengths (delta s)
    rrunlos : unloaded rotation rates (omega with line under)
    rrlos : loaded rotation rates (omega)
    fpls : force per length values (force density (K))
    leng : length of branch

'''

k = 0.005
thresholdE = 10e-3
meter = 10

class Segment(object):
    def __init__(self, leng, rrunlo, rrlo, fpl):
        self.rrunlo = rrunlo
        self.rrlo = rrlo
        self.fpl = fpl
        self.leng = leng

        self.H = 'un'
        self.F = 'un'
        self.M = 'un'
        self.pos = 'un'

def resolve(segs, pos, C):
    while True:
        oldsegs = copy.copy(segs)
        #step1
        nextH = segs[0].H
        for seg in segs:
            seg.H = nextH
            nextH += seg.rrlo*seg.leng

        #step2
        prevF = 0
        prevM = 0
        for seg in reversed(segs):
            seg.F = prevF
            seg.M = prevM

            prevF += seg.fpl*seg.leng

            prevM += np.cos(seg.H)*seg.F*seg.leng


        #step3
        maxE = 0
        for seg in segs:
            seg.E = seg.M + C*(seg.rrunlo-seg.rrlo)
            if abs(seg.E) > maxE: maxE = abs(seg.E)

        #step4
        nextpos = np.array(pos, dtype='float64') #starting position
        poslist = []
        for seg in segs:
            poslist.append(nextpos)
            seg.pos = nextpos
            nextpos = nextpos + np.array([np.cos(seg.H)*seg.leng*meter, np.sin(seg.H)*seg.leng*meter])
        poslist.append(nextpos)

        for fuckned in range(1,len(poslist)):
            pyg.draw.line(disp, (100, 30+20*fuckned, 0), poslist[fuckned-1], poslist[fuckned])
        pyg.display.update()

        if maxE > thresholdE:
            for seg, oldseg in zip(segs, oldsegs): oldseg.rrlo += k*seg.E
            segs = oldsegs
        else:
            for fuckned in range(1,len(poslist)):
                pyg.draw.line(trail, (255, 0, 0), poslist[fuckned-1], poslist[fuckned])
            disp.blit(trail,(0,0))
            pyg.display.update()
            break

dog=10
disp = pyg.display.set_mode((800, 800))
trail = pyg.Surface((800, 800))
for y in range(0, 10):
    for x in range(0,10):
        segs = []
        for i in range(dog):
            leng = 1
            rrunlo = 0
            rrlo = rrunlo
            fpl = 2
            segs.append(Segment(leng, rrunlo, rrlo, fpl))
        segs[0].H = -np.pi/2+(np.pi/5)*y
        C = (x*20)
        pos = (50+x*70, 50+y*70)
        resolve(segs, pos, C)

while True:
    disp.blit(trail, (0,0))
    pyg.display.update()



