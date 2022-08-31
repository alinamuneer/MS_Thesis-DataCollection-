#new version without a loop, just one vertex 214
import bmesh
import bpy
from bpy.props import BoolProperty
import numpy as np
import time


context = bpy.context
scene = context.scene
obj = bpy.data.objects['Cloth']
mesh = obj.data

empties = []
bpy.context.scene.frame_set(20)


empty = bpy.data.objects.new("Empty", None)

empty.parent = obj
empty.parent_type = 'VERTEX'
empty.parent_vertices = [214]*3
scene.collection.objects.link(empty)
empty.matrix_parent_inverse.identity()
empties.append((214, empty))

bpy.context.view_layer.update()

for index, empty in empties:
    bpy.ops.mesh.primitive_cube_add(size=0.1,location=(empty.matrix_world.to_translation()))
    scene.collection.objects.unlink(empty)
    bpy.data.objects.remove(empty)
bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
