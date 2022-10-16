import sys
import struct
import math

Y_horizon = 240

P_exp = [
    [(   61,   460,   700,  -300),
     (  150,   460,   700,  -200),
     (  324,   460,   700,     0),
     (  498,   460,   700,   200),
     (  587,   460,   700,   300)],
    [(   63,   390,   900,  -400),
     (  192,   390,   900,  -200),
     (  324,   390,   900,     0),
     (  456,   390,   900,   200),
     (  585,   390,   900,   400)],
    [(  116,   350,  1100,  -400),
     (  218,   350,  1100,  -200),
     (  324,   350,  1100,     0),
     (  430,   350,  1100,   200),
     (  532,   350,  1100,   400)],
    [(   62,   323,  1300,  -600),
     (  152,   323,  1300,  -400),
     (  238,   323,  1300,  -200),
     (  324,   323,  1300,     0),
     (  410,   323,  1300,   200),
     (  496,   323,  1300,   400),
     (  586,   323,  1300,   600)],
    [(   27,   302,  1500,  -800),
     (  102,   302,  1500,  -600),
     (  176,   302,  1500,  -400),
     (  251,   302,  1500,  -200),
     (  324,   302,  1500,     0),
     (  397,   302,  1500,   200),
     (  472,   302,  1500,   400),
     (  546,   302,  1500,   600),
     (  621,   302,  1500,   800)],
]

def dist(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    return math.sqrt(dx*dx+dy*dy)

P_knot = [[] for i in range(0,640)]

for pe in P_exp:
    pc_len = len(pe)
    if (pc_len<3): continue
    for i in range(0,pc_len-1):
        x0  = pe[i][0]
        y0  = pe[i][1]
        xr0 = pe[i][2]
        yr0 = pe[i][3]
        x1  = pe[i+1][0]
        y1  = pe[i+1][1]
        xr1 = pe[i+1][2]
        yr1 = pe[i+1][3]
        x_min = x0
        x_max = x1
        if i==0:
            x_min = 0
        if i==pc_len-2:
            x_max = 640
        dx = x1-x0
        dy = y1-y0
        dxr = xr1-xr0
        dyr = yr1-yr0
        if dx != 0:
            for x in range(x_min,x_max):
                y = y0 + (x-x0)*dy/dx
                Xr = xr0 + (x-x0)*dxr/dx
                Yr = yr0 + (x-x0)*dyr/dx
                #print ("{:>5d},{:>5d}".format(x,int(y)))
                P_knot[x].append((int(y),Xr,Yr))
    #print()


P_map = [[(0,0)]*480 for i in range(0,640)]
for x in range(0,640):
    Pk = P_knot[x]
    #print (Pk)
    Pk_len = len(Pk)
    if (Pk_len<3):
        continue
    for i in range(Pk_len-2,-1,-1):
        y0  = Pk[i+1][0]
        xr0 = Pk[i+1][1]
        yr0 = Pk[i+1][2]
        y1  = Pk[i][0]
        xr1 = Pk[i][1]
        yr1 = Pk[i][2]
        y_min = y0
        y_max = y1
        if i==Pk_len-2:
            y_min = Y_horizon
        if i==0:
            y_max = 480
        dy = y1-y0
        dxr = xr1-xr0
        dyr = yr1-yr0
        #print (y_min,y_max)
        if dy != 0:
            for y in range(y_min,y_max):
                Xr = xr0 + (y-y0)*dxr/dy
                Yr = yr0 + (y-y0)*dyr/dy
                P_map[x][y] = (int(Xr),int(Yr))

