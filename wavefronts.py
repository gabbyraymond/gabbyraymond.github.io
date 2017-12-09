import heapq
import math

###########################
## Parabola Computations ##
###########################

# y = (1/4*f *(x-v1)^2) + v2
# directorix: y = step
# vertex: (s_x, (s_y-f))
# focus:  (s_x, s_y)
# f:      (s_y - step)/2
def compute_para(site, step, xlist):
    f  = (site.y - step)/float(2)
    v1 = site.x 
    v2 = site.y - f
    #print "y = 1/{0} * (x-{1})^2 + {2}".format(4*f, v1, v2)
    return map((lambda x: ((x-v1)**2)/(4*f) + v2), xlist) 
    
def parabola_from_step(site,step):
    f  = (site.y - step)/float(2)
    if f == 0:
        return None # TODO handle this. Should return x = s_x a vertical line
    v1 = site.x 
    v2 = site.y - f
    a = 1/(4*f)
    b = -v1/(2*f)
    c = v1/(4*f) + v2 
    return (a,b,c)
    
#Input x-coords array, return array for parabolized x-coords
# y = ax^2 + bx + c
def parabola(xlist,(a,b,c)):
    return map((lambda x: a*(x**2) + b*2 + c), xlist)

# TODO make this return a point, not just an x coordinate
def parabola_intersection((a1,b1,c1),(a2,b2,c2)):
    a = a1-a2
    b = b1-b2
    c = c1-c2

    quad_root = b**2-4*a*c

    if a==0:
        if b!=0:
            ans = -c/b
            return [ans]
        else:
            return []
    else:
        if quad_root < 0:
            return []
        else: 
            return [(-b+math.sqrt(quad_root))/2*a, (-b-math.sqrt(quad_root))/2*a]

class Site(object):
    def __init__(self,x=0.0,y=0.0):
        self.x = x
        self.y = y

    def debug(self):
        print "Site {0}".format((self.x,self.y))

    def __cmp__(self,other):
        if self.y < other.y:
            return 1
        elif self.y > other.y:
            return -1
        elif self.x < other.x:
            return 1
        elif self.x > other.x:
            return -1
        else:
            return 0

    def distance(self,other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx*dx + dy*dy)



class Arc(object):
    def __init__(self,(x,y)):
        self.sitex = x
        self.sitey = y

    # Return arcEq at a certain time step of the sweep line
    def retArcEq(self,time):
        return parabola_from_step((self.sitex,self.sitey),time)
        


sites = map((lambda (x,y): Site(x,y)),[(0,0),(0,1),(1,1),(2,0)])

PriorityQueue = []
ArcTree = []

# Heapify on a list does not support tuples cmps, but adding individually does
for s in sites:
    heapq.heappush(PriorityQueue,s)

while PriorityQueue:
    event = heapq.heappop(PriorityQueue)
    print "popped"
    event.debug()
    time = event.y

    if event in sites:
        if not ArcTree:
            print "appending"
            ArcTree.append(event)
        else:
            for arc in ArcTree:
                curArc   = parabola_from_step(arc,time)
                eventArc = parabola_from_step(event,time)
                print "Arcs: {0} {1}".format(curArc,eventArc)
                #if curArc == None: # Line x = arcX
                #if eventArc == None: # Just have a vertical line x = eventX
                #if eventArc and curArc and parabola_intersection(eventArc,curArc):
                #    print "p_intersection! {0} & {1}".format(curArc,event.debug())
                #elif curArc and parabola([eventX],curArc):
                #    print "l_intersection! {0} & {1}".format(curArc,event.debug())
                #else: 
                #    pass
 '''
 NOTE Need to figure out where this arc should go in the list. Look at sets of
 3 adjacent arcs to see where in the linked list it should go. This requires 
 finding out what the intersection points are between adjacent arcs. Then 
 compare the intersection pt with the range of that arc at that time step. 
 '''

                    



