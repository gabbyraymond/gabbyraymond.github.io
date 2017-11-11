import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
from collections import defaultdict

v_diagram = defaultdict(list)

with open('voroni_out.txt', 'r') as f:
    for line in f:
        parts = line.split()
        v_diagram[parts[0]].append(parts[1:])
            
#Input x-coords array, return array for parabolized x-coords
# y = ax^2 + bx + c
def parabola(xlist,a,b,c):
    return map((lambda x: a*(x**2) + b*2 + c), xlist)

xlist = np.arange(-5,5,0.1)


data = [dict(
        visible = False,
        line=dict(color='00CED1', width=6),
        name = 'v = '+str(step),
        x = xlist,
        y = parabola(xlist,1,0,step)) for step in np.arange(0,10,1)]

data[1]['visible'] = True

steps = []
for i in range(len(data)):
    step = dict(
        method = 'restyle',
        args = ['visible', [False] * len(data)],
    )
    step['args'][1][i] = True # Toggle i'th trace to "visible"
    steps.append(step)

sliders = [dict(
    active = 0,
    currentvalue = {"prefix": "Frequency: "},
    pad = {"t": 10},
    steps = steps
)]

layout = dict(sliders=sliders)

fig = dict(data=data, layout=layout)

py.plot(fig, filename='Voronoi Builder')
