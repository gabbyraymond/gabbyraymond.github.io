import sys
import heapq
import math
import copy

###########################
## Parabola Computations ##
###########################
# Return top of circle and voronoi vertex given three points
# A circle is only valid if all points are distinct and do not lie on a line
def top_circle(a,b,c):
    # ensure points are distinct
    if len(set([a,b,c])) < 3:
        return None
    # ensure points aren't on a line
    if a.x == b.x: # Horizonal line test
        if a.x == c.x:
            return None
    else:
        slope = (a.y-b.y)/(a.x-b.x)
        yintercept = a.y - slope*a.x 
        if c.y == slope * c.x + yintercept:
            return None
    # line between a and b: mid_ab + k * d1
    mid_ab = Site((a.x + b.x)/2.0, (a.y + b.y)/2.0)
    d1 = Site(b.y - a.y, a.x - b.x)
    # line between a and c: mid_ac + k * d2
    mid_ac = Site((a.x + c.x)/2.0, (a.y + c.y)/2.0)
    d2 = Site(c.y - a.y, a.x - c.x)
    # intersection of both lines:
    # mid_ab + k * d1 == mid_ac + l * d2
    l = d1.x * (mid_ac.y - mid_ab.y) - d1.y * (mid_ac.x - mid_ab.x)
    if (d2.x * d1.y - d2.y * d1.x) != 0:
        l = l / (d2.x * d1.y - d2.y * d1.x)
    else: 
        print "Error at top of circle"
        return None
    center = Site(mid_ac.x + l * d2.x, mid_ac.y + l * d2.y)
    dx = center.x - a.x
    dy = center.y - a.y
    radius = math.sqrt(dx * dx + dy * dy)
    print "a: {0}\nb: {1}\nc: {2}\ncenter: {3}\nradius: {4}\ntop: {5}".format(\
            a.debug(),b.debug(),c.debug(),center.debug(),radius,(center.y-radius))
    return(Site(center.x,center.y-radius))

def circle_center(a,b,c):
    # line between a and b: mid_ab + k * d1
    mid_ab = Site((a.x + b.x)/2.0, (a.y + b.y)/2.0)
    d1 = Site(b.y - a.y, a.x - b.x)
    # line between a and c: mid_ac + k * d2
    mid_ac = Site((a.x + c.x)/2.0, (a.y + c.y)/2.0)
    d2 = Site(c.y - a.y, a.x - c.x)
    # intersection of both lines:
    # mid_ab + k * d1 == mid_ac + l * d2
    l = d1.x * (mid_ac.y - mid_ab.y) - d1.y * (mid_ac.x - mid_ab.x)
    if (d2.x * d1.y - d2.y * d1.x) != 0:
        l = l / (d2.x * d1.y - d2.y * d1.x)
    else: 
        # NOTE ignoring circle for diametric points
        l = 0
        #return None
    return Site(mid_ac.x + l * d2.x, mid_ac.y + l * d2.y)


# y = (1/4*f *(x-v1)^2) + v2
# directorix: y = step
# vertex: (s_x, (s_y-f))
# focus:  (s_x, s_y)
# f:      (s_y - step)/2
#def compute_para(site, step, xlist):
#    f  = (site.y - step)/float(2)
#    v1 = site.x 
#    v2 = site.y - f
#    #print "y = 1/{0} * (x-{1})^2 + {2}".format(4*f, v1, v2)
#    return map((lambda x: ((x-v1)**2)/(4*f) + v2), xlist) 
    
def parabola_from_step(site,step):
    f  = (site.y - step)/float(2) 
    if f == 0:
        #Should return a vertical line. For ease, use a very narrow parabola
        f = .0025 
    v1 = site.x 
    v2 = site.y - f
    a = 1/(4*f)
    b = -v1/(2*f)
    c = v1/(4*f) + v2 
    return (a,b,c)
    
#Input x-coords array, return array for parabolized x-coords
# y = ax^2 + bx + c
#def parabola_list(xlist,(a,b,c)):
#    return map((lambda x: a*(x**2) + b*x + c), xlist)

def parabola(x,(a,b,c)):
    return a*(x**2) + b*x + c

# TODO make this return a point, not just an x coordinate
def parabola_intersection((a1,b1,c1),(a2,b2,c2)):
    a = a1-a2
    b = b1-b2
    c = c1-c2

    quad_root = b**2-(4*a*c)

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
            ans = [(-b-math.sqrt(quad_root))/(2*a), (-b+math.sqrt(quad_root))/(2*a)]
            ans.sort() 
            return ans

class Site(object):
    def __init__(self,x=0.0,y=0.0):
        self.x = float(x)
        self.y = float(y)

    def debug(self):
        string = "Site {0}".format((self.x,self.y))
        return string

    def __cmp__(self,site2):
        if self.y < site2.y:
            return 1
        elif self.y > site2.y:
            return -1
        elif self.x < site2.x:
            return 1
        elif self.x > site2.x:
            return -1
        else: 
            return 0

    def __eq__(self,site2):
        return self.x == site2.x and self.y == site2.y

    def __ne__(self,site2):
        return not self.__eq__(site2)

    def __key(self):
        return (self.x, self.y)

    def __hash__(self):
        return hash(self.__key())

    def distance(self,site2):
        delta_x = self.x - site2.x
        delta_y = self.y - site2.y
        return math.sqrt(delta_x*delta_x + delta_y*delta_y)



class Arc(object):
    def __init__(self,site):
        self.site = site
        self.min_x = MIN_X #site.x
        self.max_x = MAX_X #site.x
        self.a = 0
        self.b = 0
        self.c = 0
        self.next = None
        self.prev = None

    def debug(self):
        string = "Arc y = {0}x^2 + {1}x + {2} for site {5} over the range [{3},{4}]".format(self.a,self.b,self.c,self.min_x,self.max_x,self.site.debug())
        return string

    def params(self):
        return (self.a,self.b,self.c)
    # Return arcEq at a certain time step of the sweep line
    def retArcEq(self,time):
        return parabola_from_step(self.site,time)

    def update_arc(self,time):
        # Update parameters
        (a,b,c) = parabola_from_step(self.site,time)
        self.a = a
        self.b = b
        self.c = c
        # Update bounds based on the bounding box
        bounds = parabola_intersection((a,b,c),(0,0,MAX_Y))
        if bounds:
            self.min_x = min(bounds[0],MIN_X, key=abs)
            self.max_x = min(bounds[1],MAX_X, key=abs)
        else: # Vertical line
            # This is addressed by spawning parabolas instead of vertical lines
            pass 
        # Now, update bounds based on your previous arc which has been updated already
        if self.prev:
            last_bound = parabola_intersection((a,b,c),self.prev.params())
            print "Next bounds: {0}".format(last_bound)
            if last_bound:
                self.prev.max_x = last_bound[0]
                self.min_x = last_bound[0]


# Take in 2 arcs and return spliced [arcA,arcB,arcA]
def splice_arcs(arcA,arcB):
    #print "~~~~~~~~~~~~~~~~\nsplicing update"
    #print arcA.debug()
    #print arcB.debug()
    intersections = parabola_intersection(arcA.params(),arcB.params())
    print "INTERSECTIONS {0} & {1} : {2}".format(arcA.site.debug(),arcB.site.debug(),intersections)
    if len(intersections) == 2:
        print "Splice"
        firstHalf = arcA
        secondHalf = copy.deepcopy(arcA)
        firstHalf.next = arcB 
        arcB.prev = firstHalf
        arcB.next = secondHalf
        secondHalf.prev = arcB
        firstHalf.max_x = intersections[0]
        arcB.min_x = intersections[0]
        arcB.max_x = intersections[1]
        secondHalf.min_x = intersections[1]
        return [firstHalf,arcB,secondHalf]
    if len(intersections) == 1: # arcB.max_x < arcA.max_x
        print "Half splice"
        arcB.next = arcA
        arcA.prev = arcB
        arcB.max_x = intersections[0]
        arcA.min_x = intersections[0]
        return [arcB,arcA]
    else: # Arc2 is fully to the left of Arc1
        # arcB.max_x < arcA.max_x AND arcB.min_x < arcA.min_x
        print "No splice"
        arcB.next = arcA
        arcA.prev = arcB
        return [arcB,arcA]

# Take in 3 arcs and return deleted [arcA,arcC]
def delete_arc(arcA,arcB,arcC):       
    print "~~~~~~~~~~~~~~~~\ndeleting arc"
    print arcA.debug()
    print arcB.debug()
    print arcC.debug()
    arcA.next = arcC 
    arcC.prev = arcA
    arcA.max_x = arcC.min_x
    return [arcA,arcC]

# Update wavefront ranges and insert a new Site
def update_wavefront(arcs,site,time):
    # Get equations for arcs at this time step and update current bounds
    print "Updating current arcs"
    for arc in arcs:
        arc.update_arc(time)
    for arc in arcs:
        print "At time {0} arc {6} is now y = {1}x*x + {2}x + {3} over the range [{4},{5}]".format(time,arc.a,arc.b,arc.c,arc.min_x,arc.max_x,arc.site.debug())
        
    # Add arc for site into wavefront
    newArc = Arc(site)
    print "Inserting new arc"
    newArc.update_arc(time)
    if not arcs:
        arcs.append(newArc)
        return arcs

    # Find where in the wavefront the new parabola should go
    newWave = []
    for i in range(len(arcs)):
        if arcs[i].max_x > site.x: # New site adds arc here
            updatedArcs = splice_arcs(arcs[i],newArc)
            # Add in circle events???? Need to get adjacent 
            newWave = arcs[:i] + updatedArcs + arcs[i+1:]
            break
    if not newWave: # Falls all the way to the right
        print "Add last"
        newWave = arcs + [newArc]
    return newWave

sites = map((lambda (x,y): Site(x,y)),[(0,0),(0,1),(1,1),(2,0)])
#sites = map((lambda (x,y): Site(x,y)),[(0,0),(0,1)])
#sites = map((lambda (x,y): Site(x,y)),[(0,0),(0,1),(0,-1)])
MIN_X = -5
MAX_X = 5
MAX_Y = 4
MIN_Y = -4
epsilon = sys.float_info.epsilon
PriorityQueue = []
ArcTree = []

print "\n\n\n\n\n=============================\n"
# Heapify on a list does not support tuples cmps, but adding individually does
for s in sites:
    heapq.heappush(PriorityQueue,s)

count = 0
# Iterate while sites or tops of circles
while (PriorityQueue or len(ArcTree) > 2): 
    count += 1
    if PriorityQueue:
        event = heapq.nsmallest(1,PriorityQueue)[0]
    else:
        event = Site(MAX_X,MIN_Y)
    closestToC = event
    arc_index = None 

    # Start looking at tops of circles
    if len(ArcTree) >= 3: 
        for i in range(0,len(ArcTree)-2):
            #if ArcTree[i].site != ArcTree[i+1].site and 
            if len(set([ArcTree[i].site,ArcTree[i+1].site,ArcTree[i+2].site])) == 3:
                print "Testing {0}".format([ArcTree[i].site.debug(),ArcTree[i+1].site.debug(),ArcTree[i+2].site.debug()])
                ToC = top_circle(ArcTree[i].site,ArcTree[i+1].site,ArcTree[i+2].site)
                if ToC and ToC.y > closestToC.y and ToC.y < time:
                    arc_index = i
                    closestToC = ToC
        
    # Top of Circle event is next in priority
    if closestToC.y > event.y and arc_index:
        time = closestToC.y
        print "\n******** Circle event {0} for arc {1}".format(closestToC.debug(),ArcTree[i].debug())
        print "Voronoi vertex: {0})".format(circle_center(ArcTree[arc_index].site,ArcTree[arc_index+1].site,ArcTree[arc_index+2].site).debug())
        print "   Removing {0} at arc index {1}".format(ArcTree[arc_index+1].debug(),arc_index+1)
        NewArcTree = ArcTree[:arc_index] +\
                  delete_arc(ArcTree[arc_index],ArcTree[arc_index+1],ArcTree[arc_index+2])
        if arc_index+2 < len(ArcTree):
            print "adding rest of list"
            NewArcTree += ArcTree[arc_index+3:]
            for arc in ArcTree[arc_index+3:]:
                print arc.debug()
        ArcTree = NewArcTree
    # Site event is next in priority 
    elif PriorityQueue: 
        event = heapq.heappop(PriorityQueue)
        print "\n******** Site event {0}".format(event.debug())
        time = event.y
        ArcTree = update_wavefront(ArcTree,event,time)
    else:
        break
    print len(ArcTree)
    for arc in ArcTree:
        print arc.debug()


print "\n\n=============================\n"
