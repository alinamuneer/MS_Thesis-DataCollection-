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
print(obj.data.polygons[858].normal)
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
bpy.data.objects['Cloth'].select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects['Cloth']
bpy.ops.object.mode_set(mode = 'EDIT')
bm = bmesh.from_edit_mesh(mesh)
bpy.ops.mesh.normals_make_consistent()
bm.faces.ensure_lookup_table()
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[858:])
print(bm.faces[858].normal)
bpy.ops.object.mode_set(mode = 'OBJECT')

#the code to convert current frame into a new mesh
context = bpy.context
scene = context.scene
obj = bpy.data.objects['Cloth']
mesh = obj.data
bpy.ops.object.convert(target='MESH', keep_original=True)
obj = bpy.data.objects['Cloth_new']
obj = bpy.data.objects['Cloth']
obj_new = bpy.data.objects['Cloth_new']
mesh_new = obj_new.data
print(obj.data.polygons[858].normal)
<Vector (0.3656, -0.4837, 0.7952)>

print(obj_new.data.polygons[858].normal)
<Vector (-0.8503, 0.1995, -0.4870)>
