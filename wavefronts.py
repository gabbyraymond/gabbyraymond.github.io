import sys
import heapq
import math
import copy
import plotly.plotly as py
import plotly.graph_objs as go

###########################
## Parabola Computations ##
###########################
# Return top of circle and voronoi vertex given three points
# A circle is only valid if all points are distinct and do not lie on a line
# TODO replace with circle class defined below
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
    #if debug:
        #print "a: {0}\nb: {1}\nc: {2}\ncenter: {3}\nradius: {4}\ntop: {5}".format(\
        #        a.debug(),b.debug(),c.debug(),center.debug(),radius,(center.y-radius))
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
    
# TODO put this under Site class
def parabola_from_step(site,step):
    f  = (site.y - step)/float(2) 
    if f == 0:
        #Should return a vertical line. For ease, use a very narrow parabola
        f = .0025 
    v1 = site.x 
    v2 = site.y - f
    a = 1/(4*f)
    b = -v1/(2*f)
    c = (v1**2)/(4*f) + v2 
    return (a,b,c)
    
#Input x-coords array, return array for parabolized x-coords
# y = ax^2 + bx + c
#def parabola_list(xlist,(a,b,c)):
#    return map((lambda x: a*(x**2) + b*x + c), xlist)


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
        self.radius = .01
        self.min_y = self.y - self.radius 
        self.max_y = self.y + self.radius
        self.min_x = self.x - self.radius 
        self.max_x = self.x + self.radius
        self.plotly_shape = { 
            'type': 'circle',
            'xref': 'x',
            'yref': 'y',
            'x0': self.min_x,
            'y0': self.min_y,
            'x1': self.max_x,
            'y1': self.max_y,
            'line': { 'color': 'orange' },
            'fillcolor': { 'color': 'orange' }
            # line weight?
            }


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

#class State(object):
#    def __init__(self,event,time,arcs):
#        if type(event) == Site:
#            self.flag = "Site"
#        else:
#            self.flag = "Circle"
#        self.event = event 
#        self.time = time
#        self.arcs = arcs 



class Circle(object):
    def __init__(self,p1,p2,p3):
        self.p1 = p1 
        self.p2 = p2 
        self.p3 = p3
        (center, radius) = self.compute_circle(p1,p2,p3)
        self.center = center 
        self.radius = radius 
        self.min_y = self.center.y - self.radius 
        self.max_y = self.center.y + self.radius
        self.min_x = self.center.x - self.radius 
        self.max_x = self.center.x + self.radius
        self.plotly_shape = { 
            'type': 'circle',
            'xref': 'x',
            'yref': 'y',
            'x0': self.min_x,
            'y0': self.min_y,
            'x1': self.max_x,
            'y1': self.max_y,
            'line': { 'color': 'orange' }
            }
        # TODO add circle center?

    def debug():
        string = "p1: {0} p2: {1} p3: {2}".format(\
                self.p1.debug(),self.p2.debug(),self.p3.debug())
        string2 = "center: {3} radius: {4} top: {5}".format(\
                  self.center.debug(),self.radius,self.min_y)
        return string1 + '\n' + string2

    # A circle is only valid if all points are distinct and do not lie on a line
    def compute_circle(self,a,b,c):
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
        return (center, radius)


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
        string = "Arc y = {0}x^2 + {1}x + {2} for {5} over [{3},{4}]".format(\
                  self.a,self.b,self.c,self.min_x,self.max_x,self.site.debug())
        return string
    
    def make_plotly(self): # Add time in??? FIXME
        xs = make_range(self.min_x,self.max_x)
        ys = map((lambda x: self.parabola_func(x)), xs)
        return (xs,ys)

    def parabola_func(self,x):
        val = self.a*(x**2) + self.b*x + self.c
        return min(val, MAX_Y) 

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
            bounds = parabola_intersection((a,b,c),self.prev.params())
            # If prev intersects this arc twice, make sure to use right bound
            # for second time it intersects. Prevent an arc from not having any
            # width.
            if bounds[0] == self.prev.min_x: 
                self.prev.max_x = bounds[1]
                self.min_x = bounds[1]
            else:
                self.prev.max_x = bounds[0]
                self.min_x = bounds[0]

class ArcList(object):
    def __init__():
        self.arcs = []

# Take in 2 arcs and return spliced [arcA,arcB,arcA]
def splice_arcs(arcA,arcB):
    #if debug:
        #print "~~~~~~~~~~~~~~~~\nsplicing update"
        #print arcA.debug()
        #print arcB.debug()
    intersections = parabola_intersection(arcA.params(),arcB.params())
    if debug:
        print "INTERSECTIONS {0} & {1} : {2}".format(arcA.site.debug(),arcB.site.debug(),intersections)
    # TODO TODO need class for ArcList or voronoi to prevent having to know all arcs involved, ugg
   # if arcA.prev and top_circle(arcA.prev.site,arcA.site,arcB.site)
   #     print "left voila!"
   #     # Right
   #     if arcA.site < arcB.site:
   #         arcB.next = arcA.next
   #         arcB.prev = arcA
   #         arcA.next = arcB 
   #         return [arcA,arcB]
   #     # Mid
   #     elif arcA.prev < arcB.site:
   #         arcB.next = arcA
   #         arcB.prev = arcA.prev
   #         arcA.prev.next = arcB 
   #     # Left
   #     else
   #         arcB.next = arcA.prev 
   #         arcB.prev = arcA.prev.prev 
   #         arcA.prev.prev = arcB
   # if arcA.next and top_circle(arcA.next.site,arcA.site,arcB.site)
   #     print "right voila!"
   #     exit(0)
    if len(intersections) == 2:
        if debug:
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
        if debug:
            print "Half splice"
        arcB.next = arcA
        arcA.prev = arcB
        arcB.max_x = intersections[0]
        arcA.min_x = intersections[0]
        return [arcB,arcA]
    else: # Arc2 is fully to the left of Arc1
        # arcB.max_x < arcA.max_x AND arcB.min_x < arcA.min_x
        if debug:
            print "No splice"
        arcB.next = arcA
        arcA.prev = arcB
        return [arcB,arcA]

# Take in 3 arcs and return deleted [arcA,arcC]
def delete_arc(arcA,arcB,arcC):       
    arcA.next = arcC 
    arcC.prev = arcA
    mid = (arcB.max_x - arcB.min_x)/2.0 + arcB.min_x
    arcA.max_x = mid 
    arcC.min_x = mid
    #if debug:
    #    print "~~~~~~~~~~~~~~~~\ndeleting arc"
    #    print arcA.debug()
    #    #print arcB.debug()
    #    print arcC.debug()
    #    print "~~~~~~~~~ midpoint {0}".format(mid)
    return [arcA,arcC]

# Update wavefront ranges and insert a new Site
def update_wavefront(arcs,site,time):
    # Get equations for arcs at this time step and update current bounds
    #print "Updating current arcs"
    for arc in arcs:
        arc.update_arc(time)
    #if debug:
    #    print "updated prev arcs"
    #    for arc in arcs:
    #        print "At time {0} arc {6} is now y = {1}x*x + {2}x + {3} over the range [{4},{5}]".format(time,arc.a,arc.b,arc.c,arc.min_x,arc.max_x,arc.site.debug())
    #        if arc.prev and arc.next:
    #            print "    - arc has prev {0} and next {1}".format(arc.prev.site.debug(),arc.next.site.debug())
        
    # Add arc for site into wavefront
    newArc = Arc(site)
    if debug:
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
            if debug:
                print "New arcs"
                for arc in updatedArcs:
                    print "  -> {0}".format(arc.debug())
            # Add in circle events???? Need to get adjacent 
            newWave = arcs[:i] + updatedArcs + arcs[i+1:]
            break
    if not newWave: # Falls all the way to the right
        if debug:
            print "Add last"
        newWave = arcs + [newArc]
    return newWave

def dump_plotly(states):
    import matplotlib.pyplot as pyplt
    data = []
    shapes = []
    #for s in states[-1:]:
    print type(states)
    s = states[3]
    if True:
        print s
        xs = []
        ys = []
        # TODO need to do this for each time step in slider!
        for arc in s['arcs']:
            print arc.debug()
            (arc_xs,arc_ys) = arc.make_plotly()
            print arc_xs 
            print arc_ys
            print '\n'
            xs.extend(arc_xs)
            ys.extend(arc_ys)
        data.append({
            'x': xs,
            'y': ys,
            'line': {'color': 'black'},#, 'width': 4},
            'mode': 'lines',
            'name': arc.site.debug(),
            'type': 'scatter'
            })
        #shapes.append(s['event'].plotly_shape)
        print "--- All coords ---"
        print xs 
        print ys
        pyplt.figure()
        pyplt.plot(xs, ys)
        pyplt.show()

    layout = {\
        #'xaxis': {'range': [MIN_X,MAX_X]}, 
        #'yaxis': {'range': [MIN_Y,MAX_Y]},
        #'shapes': shapes
        }
    fig = dict(data=data,layout=layout)
    # NOTE currently drawing over itself (that's why it's going back to the
    # start. Plotted the first parabola correctly, not sure why other states are difficult
    #py.plot(fig,filename='Wavefronts')

def make_range(start,stop,step=0.05):
    nums = []
    temp = start
    while temp < stop:
        nums.append(temp)
        temp += step
    nums.append(stop)
    return nums

#sites = map((lambda (x,y): Site(x,y)),[(0.6,1.62),(1,3),(-1,3.5),(0,2),(0,2.5)])
#sites = map((lambda (x,y): Site(x,y)),[(0,1),(2,0),(1,1),(0,0)])
#sites = map((lambda (x,y): Site(x,y)),[(0,0),(0,1)])
# FIXME broken case
#sites = map((lambda (x,y): Site(x,y)),[(1,0),(0,1),(0,-1)])
sites = map((lambda (x,y): Site(x,y)),[(1,0),(0,1),(-1,0)])
MIN_X = -5
MAX_X = 5
MAX_Y = 5
MIN_Y = -5
epsilon = sys.float_info.epsilon
PriorityQueue = []
StateList = []
# Better if this is in the form of a tree
ArcList = []
debug = True
#debug = False 

if debug:
    print "\n\n\n\n\n=============================\n"
# Heapify on a list does not support tuples cmps, but adding individually does
# FIXME need to make sure sites are unique on reading
for s in sites:
    heapq.heappush(PriorityQueue,s)


# Iterate while sites or tops of circles
while (PriorityQueue or len(ArcList) > 2): 
    if debug:
        print "\n~~~~~\n"
    if PriorityQueue:
        event = heapq.nsmallest(1,PriorityQueue)[0]
    else:
        event = Site(MAX_X,MIN_Y)
    closestToC = event
    arc_index = None 

    # Start looking at tops of circles
    if len(ArcList) >= 3: 
        for i in range(1,len(ArcList)-1):
            # Make sure to delete arc 1 if site is in the middle of prev and next
            if ArcList[i-1].site.x <= ArcList[i].site.x and\
               ArcList[i].site.x <= ArcList[i+1].site.x:
                # Make sure we have distinct points
                if len(set([ArcList[i-1].site,ArcList[i].site,ArcList[i+1].site])) == 3:
                    ToC = top_circle(ArcList[i-1].site,ArcList[i].site,ArcList[i+1].site)
                    if debug:
                        print "Testing {0}".format([ArcList[i-1].site.debug(),\
                               ArcList[i].site.debug(),ArcList[i+1].site.debug()])
                        print "ToC {0}".format(ToC.debug())
                    if ToC and ToC.y > closestToC.y and ToC.y <= time:
                        arc_index = i
                        closestToC = ToC
        
    # Top of Circle event is next in priority
    if closestToC.y > event.y or not PriorityQueue and arc_index:
        time = closestToC.y
        circle = Circle(ArcList[arc_index-1].site,ArcList[arc_index].site,ArcList[arc_index+1].site)

        for arc in ArcList:
            arc.update_arc(time)
        
        if debug:
            print "\n******** Circle event {0} \n\tfor arc {1}".format(\
                    closestToC.debug(),ArcList[arc_index].debug())
            print "   Voronoi vertex: {0})".format(circle.center.debug())
            print "   Removing {0} at arc index {1}".format(ArcList[arc_index].debug(),arc_index)
        print "v {:.6f} {:.6f}".format(circle.center.x,circle.center.y)
        # Would be nice if this acted on the list TODO
        NewArcList = ArcList[:arc_index-1] +\
                  delete_arc(ArcList[arc_index-1],ArcList[arc_index],ArcList[arc_index+1])
        if arc_index+1 < len(ArcList):
            #print "adding rest of list"
            NewArcList += ArcList[arc_index+2:]
            #for arc in ArcList[arc_index+2:]:
            #    print arc.debug()
        ArcList = NewArcList
        StateList.append({'event': circle, 'y': time, 'arcs':copy.deepcopy(ArcList)})


    # Site event is next in priority 
    elif PriorityQueue: 
        event = heapq.heappop(PriorityQueue)
        if debug:
            print "\n******** Site event {0}".format(event.debug())
        time = event.y
        ArcList = update_wavefront(ArcList,event,time)
        StateList.append({'event': event, 'y': time, 'arcs':copy.deepcopy(ArcList)})
    else:
        break
    if debug:
        print len(ArcList)
        for arc in ArcList:
            print arc.debug()
#if debug:
#    print "/////////// States \\\\\\\\\\\\"
#    for s in StateList:
#        print s
    

#dump_plotly(StateList)

if debug:
    print "\n\n=============================\n"
