import math
import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
from collections import defaultdict

##############################
## Get input from text file ##
##############################

v_diagram = defaultdict(list)

with open('voronoi_out.txt', 'r') as f:
    for line in f:
        parts = line.split()
        v_diagram[parts[0]].append(map((lambda x: float(x)),parts[1:]))

# Plot voronoi sites
data = [
    Scatter(
        x=site_xs,
        y=site_ys,
        name = "sites",
        mode = "markers"
)]


##################################
## Set variables based on input ##
##################################

granularity    = 20 # Calibrate smoothness of parabolas
num_data_steps = 10 # Keep track of how many steps we're showing
num_data_other = 1  # Keep track of auxiliary datasets in the list
site_xs=list(zip(*v_diagram['s'])[0]) # Unzip list of points into
site_ys=list(zip(*v_diagram['s'])[1]) # list of site coordinates
max_y = math.ceil(max(site_ys) + np.std(site_ys))
min_y = math.floor(min(site_ys) - np.std(site_ys))
max_x = math.ceil(max(site_xs) + np.std(site_xs))
min_x = math.floor(min(site_xs) - np.std(site_xs))
y_range = np.arange(min_y, max_y, (max_y-min_y)/float(num_data_steps))
x_range = np.arange(min_x, max_x, (max_x-min_x)/float(granularity))


###########################
## Parabola Computations ##
###########################

# y = (1/4*f *(x-v1)^2) + v2
# directorix: y = step
# vertex: (s_x, (s_y-f))
# focus:  (s_x, s_y)
# f:      (s_y - step)/2
def compute_para((s_x, s_y), step, xlist):
    f  = (s_y - step)/float(2)
    v1 = s_x 
    v2 = s_y - f
    print "y = 1/{0} * (x-{1})^2 + {2}".format(4*f, v1, v2)
    return map((lambda x: ((x-v1)**2)/(4*f) + v2), xlist) 
    

#Input x-coords array, return array for parabolized x-coords
# y = ax^2 + bx + c
def parabola(xlist,a,b,c):
    return map((lambda x: a*(x**2) + b*2 + c), xlist)


def parabola_intersection(a1,a2,b1,b2,c1,c2):
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

####################
## Plot parabolas ##
####################

step_data = [dict(
        visible = False,
        line=dict(color='00CED1', width=6),
        name = str(step),
        x = x_range,
        y = compute_para((0,1),step,x_range)) for step in y_range[::-1]]


data.extend(step_data)


steps = []
for i in range(len(data)):
    step = dict(
        method = 'restyle',
        args = ['visible', [True] * num_data_other + [False] * num_data_steps],
    )
    step['args'][1][i] = True # Toggle i'th trace to "visible"
    steps.append(step)

sliders = [dict(
    active = 0,
    currentvalue = {"prefix": "Frequency: "},
    pad = {"t": 10},
    steps = steps
)]

####################
## Construct Plot ##
####################

layout = dict(sliders=sliders)

fig = dict(data=data, layout=layout)

py.plot(fig, filename='Voronoi Builder')
