import sys
import heapq
import math
import copy
import plotly.plotly as py
import plotly.graph_objs as go

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
            ans = [(-b-math.sqrt(quad_root))/(2*a), 
                   (-b+math.sqrt(quad_root))/(2*a)]
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


class Circle(object):
    def __init__(self,p1,p2,p3):
        self.p1 = p1 
        self.p2 = p2 
        self.p3 = p3
        circle_info = None
        # Three distinct points?
        if len(set([p1,p2,p3])) == 3:
            circle_info = self.compute_circle(p1,p2,p3)
        if circle_info:
            self.center = circle_info[0]
            self.radius = circle_info[1]
            self.min_y = self.center.y - self.radius 
            self.max_y = self.center.y + self.radius
            self.min_x = self.center.x - self.radius 
            self.max_x = self.center.x + self.radius
            self.ToC = Site(self.center.x,self.min_y)
            self.y = self.min_y
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
        else:
            self.center = None 
            self.radius = None 
            self.ToC = None

    def debug(self):
        return self.ToC.debug()

    def info(self):
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
    
    def make_plotly(self): # Add time in for steps??? FIXME
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

class Arcs(object):
    def __init__(self):
        self.arcs = []

    def length(self):
        return len(self.arcs)
    
    # insert arc at index, shifting everything afterwards 
    def insert(self,index,arc):
        if not self.arcs:
            self.arcs.append(arc)
        else:
            tempList = self.arcs[:index] + [arc] + self.arcs[index:]
            if index != 0:
                arc.prev = self.arcs[index-1]
                arc.prev.next = arc
            else:
                arc.prev = None
            if index < self.length():
                arc.next = self.arcs[index]
                arc.next.prev = arc
            else:
                arc.next = None
            self.arcs = tempList

    # Splice arcB with arcA at given index
    def splice_arcs(self,index,arcB):
        arcA = self.arcs[index]
        intersections = parabola_intersection(arcA.params(),arcB.params())
        if debug:
            print "INTERSECTIONS {0} & {1} : {2}".format(arcA.site.debug(),arcB.site.debug(),intersections)
        # TODO TODO 
       # if arcA.prev and Circle(arcA.prev.site,arcA.site,arcB.site)
       #     print "left voila!"
       #     # Right
       #     if arcA.site < arcB.site:
       #         arcB.next = arcA.next
       #         arcB.prev = arcA
       #         arcA.next = arcB 
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
       # if arcA.next and Circle(arcA.next.site,arcA.site,arcB.site)
       #     print "right voila!"
       #     exit(0)
        if len(intersections) == 2:
            if debug:
                print "Splice"
            secondHalf = copy.deepcopy(arcA)
            arcA.max_x = intersections[0]
            arcB.min_x = intersections[0]
            arcB.max_x = intersections[1]
            secondHalf.min_x = intersections[1]
            self.insert(index+1,arcB) # Now arcB resides at index
            self.insert(index+2,secondHalf) # Place secondHalf right after arcB

        else:
            if len(intersections) == 1: 
                if debug:
                    print "Half splice"
                arcB.max_x = intersections[0]
                arcA.min_x = intersections[0]
            if arcB.site > arcA.site: # Insert to the left. 
                #Note that cmp is intentionally backwards
                self.insert(index,arcB)
            else:                     # Insert to the right
                self.insert(index+1,arcB)

    # Take in arc index to be delete 
    def delete(self,index):
        badArc = self.arcs[index]
        if debug:
            print badArc.debug()
        tempList = self.arcs[:index] + self.arcs[index+1:]
        mid = (badArc.max_x - badArc.min_x)/2.0 + badArc.min_x
        if badArc.prev:
            badArc.prev.next = badArc.next 
            badArc.prev.max_x = mid
        if badArc.next:
            badArc.next.min_x = mid
            badArc.next.prev = badArc.prev 
        self.arcs = tempList
        if debug:
            print "~~~~~~~~~ midpoint {0}".format(mid)


    def update_all(self,time):
        for arc in self.arcs:
            arc.update_arc(time)
        if len(self.arcs) == 2:
            arc1 = self.arcs[0]
            arc2 = self.arcs[1]
            bounds = parabola_intersection(arc1.params(),arc2.params())
            if bounds:
                arc1.max_x = bounds[0]
                arc2.min_x = bounds[0]

        # Find all triples
        for arc1,arc2,arc3 in zip(self.arcs,self.arcs[1:],self.arcs[2:]):
            # Case where arc2 is spliced
            if arc1.site == arc3.site:
                bounds = parabola_intersection(arc1.params(),arc2.params())
                if bounds:
                    arc1.max_x = bounds[0]
                    arc2.min_x = bounds[0]
                    arc2.max_x = bounds[1]
                    arc3.min_x = bounds[1]
            else:
                left_bounds = parabola_intersection(arc1.params(),arc2.params())
                right_bounds = parabola_intersection(arc2.params(),arc3.params())
                if len(left_bounds) == 1:
                    arc1.max_x = left_bounds[0]
                    arc2.min_x = left_bounds[0]
                elif len(left_bounds) ==2:
                    arc1.max_x = left_bounds[1]
                    arc2.min_x = left_bounds[1]
                if right_bounds: 
                    arc2.max_x = right_bounds[0]
                    arc3.min_x = right_bounds[0]
            #if debug:
            #    print "______Triple______"
            #    print arc1.debug()
            #    print arc2.debug()
            #    print arc3.debug()


    # Update wavefront ranges and insert a new Site
    def update_wavefront(self,site,time):
        # Get equations for arcs at this time step and update current bounds
        #print "Updating current arcs"
        self.update_all(time)
        if debug:
            print "updated prev arcs"
            for arc in self.arcs:
                print "At time {0} arc {6} is now y = {1}x*x + {2}x + {3} over the range [{4},{5}]".format(\
                time,arc.a,arc.b,arc.c,arc.min_x,arc.max_x,arc.site.debug())
                if arc.prev: 
                    print " - arc has prev {0}".format(arc.prev.site.debug())
                if arc.next:
                    print " - arc has next {0}".format(arc.next.site.debug())
            
        # Add arc for site into wavefront
        newArc = Arc(site)
        if debug:
            print "Inserting new arc"
        newArc.update_arc(time)
        if self.arcs:
            # Find where in the wavefront the new parabola should go
            for i in range(len(self.arcs)):
                if debug:
                    print "Checking arc {0} {1} {4} >? {2} {3}".format(i,\
                           self.arcs[i].site.debug(),
                           site.x,self.arcs[i].max_x >site.x,
                           self.arcs[i].max_x)
                if self.arcs[i].max_x > site.x: # New site adds arc here
                    self.splice_arcs(i,newArc)
                    if debug:
                        print "New arcs, spliced in {0}".format(i)
                        for arc in self.arcs:
                            print "  -> {0}".format(arc.debug())
                    # Add in circle events???? Need to get adjacent 
                    break
                elif i == len(self.arcs)-1: # Falls all the way to the right
                    if debug:
                        print "Add last"
                    self.insert(i,newArc)
                    break
        else:
            self.arcs.insert(0,newArc)
            return

    def find_next_circle_event(self,time,event):
        closestToC = event
        arc_index = None 
        if self.length() >= 3: 
            for i in range(1,self.length()-1):
                # Make sure to delete arc 1 if site is in the middle of prev and next
                p1 = self.arcs[i-1].site
                p2 = self.arcs[i].site
                p3 = self.arcs[i+1].site
                if p1.x <= p2.x and p2.x <= p3.x:
                    circle = Circle(p1,p2,p3)
                    if circle.center:
                        ToC = circle.ToC
                        if debug:
                            print "Testing {0}".format([p1.debug(),\
                                   p2.debug(),p3.debug()])
                            print "ToC {0} > {1} and {0} < {2}".format(ToC.y,closestToC.y,time-epsilon)
                        if ToC and ToC.y > closestToC.y and ToC.y < time-epsilon:
                            arc_index = i
                            closestToC = ToC
        return (closestToC, arc_index)
        
def dump_plotly(states):
    import matplotlib.pyplot as pyplt
    data = []
    shapes = []
    steps = []
    for s in states:
        print s
        xs = []
        ys = []
        # TODO need to do this for each time step in slider!
        for arc in s['arcs'].arcs:
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
            'name': s['event'].y,
            'type': 'scatter'
            })
        shapes.append(s['event'].plotly_shape)
        step = make_step(data,state) 
        #pyplt.figure()
        #pyplt.plot(xs, ys)
        #pyplt.show()

    layout = {\
        'width': 950,
        'height': 800,
        'xaxis': {'range': [MIN_X,MAX_X]}, 
        'yaxis': {'range': [MIN_Y,MAX_Y]},
        'shapes': shapes
        }
    fig = dict(data=data,layout=layout,frames=frames)
    py.plot(fig,filename='Wavefronts')



def make_range(start,stop,step=0.01):
    nums = []
    temp = start
    while temp < stop:
        nums.append(temp)
        temp += step
    nums.append(stop)
    return nums

#sites = map((lambda (x,y): Site(x,y)),[(0.6,1.62),(1,3),(-1,3.5),(0,2),(0,2.5)])
sites = map((lambda (x,y): Site(x,y)),[(0,1),(2,0),(1,1),(0,0)])
#sites = map((lambda (x,y): Site(x,y)),[(0,0),(0,1)])
# FIXME broken case
#sites = map((lambda (x,y): Site(x,y)),[(1,0),(0,1),(0,-1)])
#sites = map((lambda (x,y): Site(x,y)),[(1,0),(0,1),(-1,0)])
#sites = map((lambda (x,y): Site(x,y)),[(1,0)])
MIN_X = -5
MAX_X = 5
MAX_Y = 5
MIN_Y = -5
time = MAX_Y
epsilon = 0.00001
PriorityQueue = []
StateList = []
# Better if this is in the form of a tree
ArcList = Arcs()
debug = True
debug = False 

if debug:
    print "\n\n\n\n\n=============================\n"
# Heapify on a list does not support tuples cmps, but adding individually does
# FIXME need to make sure sites are unique on reading
for s in sites:
    heapq.heappush(PriorityQueue,s)


# Iterate while sites or tops of circles
while (PriorityQueue or ArcList.length() > 2): 
    if debug:
        print "\n~~~~~ last time was: {0}\n".format(time)
    if PriorityQueue:
        event = heapq.nsmallest(1,PriorityQueue)[0]
    else:
        event = Site(MAX_X,MIN_Y)


    (closestToC,arc_index) = ArcList.find_next_circle_event(time,event)
    if debug:
        print "next Toc: {0}".format(closestToC.y)
        
    # Top of Circle event is next in priority
    
    if debug:
        print "Time: {0} < ToC: {1} < Event: {2}".format(time-epsilon,closestToC.y,event.y-epsilon)
    if closestToC.y > event.y\
       and closestToC.y < (time-epsilon)\
       and arc_index:
        time = closestToC.y
        circle = Circle(ArcList.arcs[arc_index-1].site,
                        ArcList.arcs[arc_index].site,
                        ArcList.arcs[arc_index+1].site)

        ArcList.update_all(time)

        if debug:
            print "\n******** Circle event {0} \n\tfor arc {1}".format(\
                    closestToC.debug(),ArcList.arcs[arc_index].debug())
            print "   Voronoi vertex: {0})".format(circle.center.debug())
            print "   Removing {0} at arc index {1}".format(ArcList.arcs[arc_index].debug(),arc_index)
        print "v {:.6f} {:.6f}".format(circle.center.x,circle.center.y)
        # Would be nice if this acted on the list TODO
        ArcList.delete(arc_index)
        StateList.append({'event': circle, 'y': time, 'arcs':copy.deepcopy(ArcList)})


    # Site event is next in priority 
    elif PriorityQueue: 
        event = heapq.heappop(PriorityQueue)
        if debug:
            print "\n******** Site event {0}".format(event.debug())
        time = event.y
        ArcList.update_wavefront(event,time)
        StateList.append({'event': event, 'y': time, 'arcs':copy.deepcopy(ArcList)})
    else:
        break
    if debug:
        print ArcList.length()
        for arc in ArcList.arcs:
            print arc.debug()
if debug:
    print "/////////// States \\\\\\\\\\\\"
    for s in StateList:
        print s
    


if debug:
    print "\n\n=============================\n"



def dump_plotly2(states):
    data = []
    shapes = []
    steps = [s['event'].y for s in states]

    figure = {
    'data': [],
    'layout': {},
    'frames': []
    }

    figure['layout']['sliders'] = {
        'args': [
            'transition', {
                'duration': 400,
                'easing': 'cubic-in-out'
            }
        ],
        'initialValue': MAX_Y,
        'plotlycommand': 'animate',
        'values': steps,
        'visible': True
    }
    figure['layout']['updatemenus'] = [
        {
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 500, 'redraw': False},
                            'fromcurrent': True, 
                            'transition': {'duration': 300, 
                                           'easing': 'quadratic-in-out'}}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 
                                      'mode': 'immediate',
                                      'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }
    ]
    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Sweep Line:',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': []
    }

    # Make data
    time = MAX_Y 
    data_dict = { 'x': [site.x for site in sites],
                  'y': [site.y for site in sites],
                  'mode': 'markers'
                  }
    figure['data'].append(data_dict)
   # for s in states:
   #     print s
   #     xs = []
   #     ys = []
   #     for arc in s['arcs'].arcs:
   #         (arc_xs,arc_ys) = arc.make_plotly()
   #         xs.extend(arc_xs)
   #         ys.extend(arc_ys)
   #     data_dict = {
   #         'x': xs,
   #         'y': ys,
   #         'line': {'color': 'black'},#, 'width': 3},
   #         'mode': 'lines',
   #         'name': s['event'].y,
   #         'type': 'scatter'
   #         }
   #     shapes.append(s['event'].plotly_shape)
   #     figure['data'].append(data_dict)

    
    # make frames
    for s in states:
        time = s['event'].y
        frame = {'data': [], 'name': str(time)}
        xs = []
        ys = []
        for arc in s['arcs'].arcs:
            (arc_xs,arc_ys) = arc.make_plotly()
            xs.extend(arc_xs)
            ys.extend(arc_ys)
        data.append({
            'x': xs,
            'y': ys,
            'line': {'color': 'black'},#, 'width': 3},
            'mode': 'lines',
            'name': time,
            'type': 'scatter'
            })
        frame['data'].append(data_dict)
        figure['frames'].append(frame)
        slider_step = {'args': [[time],
                                {'frame': {'duration': 300, 'redraw': False},
                                 'mode': 'immediate',
                                 'transition': {'duration': 300}}
                                ],
                        'label': time,
                        'method': 'animate'}
        sliders_dict['steps'].append(slider_step)



    figure['layout']['width']  = 850
    figure['layout']['height'] = 700
    #figure['layout']['xaxis']  = {'range': [MIN_X,MAX_X]}, 
    #figure['layout']['yaxis']  = {'range': [MIN_Y,MAX_Y]},
    figure['layout']['shapes'] = shapes
    figure['layout']['sliders'] = [sliders_dict]
    figure['data'] = data

    py.plot(figure,filename='Wavefronts')



#dump_plotly2(StateList)
