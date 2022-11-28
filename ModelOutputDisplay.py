import bmesh
import bpy
from bpy.props import BoolProperty
import numpy as np
import time
from math import radians
import pandas as pd


#df=pd.read_csv('../blender/blender-3.2.1-linux-x64/DataCollection-REDfirst/OGP_dataset_collection_RED.csv', names=['image_name', 'x', 'y', 'z','w','X', 'Y', 'Z'], header=None)

#FINDING MAX AND MIN
#max_x=df['x'].max()
#min_x=df['x'].min()

#max_y=df['y'].max()
#min_y=df['y'].min()

#max_z=df['z'].max()
#min_z=df['z'].min()

#max_w=df['w'].max()
#min_w=df['w'].min()

#max_X=df['X'].max()
#min_X=df['X'].min()

#max_Y=df['Y'].max()
#min_Y=df['Y'].min()

#max_Z=df['Z'].max()
#min_Z=df['Z'].min()

#print(max_x,max_y,max_z,max_w,max_X,max_Y,max_Z)

Max_array=[0.9889544750987916, 0.3939566433348853, 0.2124476408428167, -0.0650312287270237, 0.3680083743045663, -0.0452284944462277, -1.321526643739921]
Min_array=[0.8779748237221331, -0.2829904591975071, -0.2640630821842629, -0.3773745499422711, -0.6752321373925586, -0.4508466892495639, -1.6952582146467725]

#these are normalized outputs
#-RightRotation0.0-location-0.03533010184764862-frame20-energy0.8Camera.026depth.png
#-RightRotation0.0-location-0.03533010184764862-frame30-energy0.2Camera.021depth.png
#-RightRotation0.0-location-0.03533010184764862-frame50-energy0.8Camera.023depth.png

A=[0.6549, 0.2647, 0.9492, 0.5193, 0.3679, 0.8355, 0.8057]
B=[0.9892, 0.4804, 0.6172, 0.7255, 0.5124, 0.8508, 0.8705]
C=[0.0018, 1.1141, 0.0269, 1.0371, 0.7785, 0.7579, 0.5677]

#print(Max_array,Min_array)
for i in range(len(A)):
   A[i] = (A[i]*(Max_array[i]-Min_array[i]))+Min_array[i]
   B[i] = (B[i]*(Max_array[i]-Min_array[i]))+Min_array[i]
   C[i] = (C[i]*(Max_array[i]-Min_array[i]))+Min_array[i]




bpy.ops.mesh.primitive_cube_add(size=0.01, location=(A[4], A[5], A[6]))
bpy.ops.mesh.primitive_cube_add(size=0.03, location=(B[4], B[5], B[6]))
bpy.ops.mesh.primitive_cube_add(size=0.06, location=(C[4], C[5], C[6]))



