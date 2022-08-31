import bpy
from bpy.props import BoolProperty
import numpy as np
import bmesh

#me = ob.to_mesh()
#me.update()
#me.calc_normals()
#me.transform(ob.matrix_world)

#bpy.ops.mesh.primitive_cube_add(size=0.1, location=(me.polygons[858].normal * 10 ))
#ob.to_mesh_clear()
bpy.context.scene.frame_start = 50

def my_handler(scene):
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus

        bpy.context.view_layer.update()
        
        context = bpy.context
        scene = context.scene

        bm = bmesh.new()   # create an empty BMesh

        ob = bpy.data.objects['Cloth']
        #bpy.context.scene.frame_set(80)

        bm.from_mesh(ob.data) 

        rme=bpy.data.meshes.new("Rib")
        bm.to_mesh(rme)

        copy = bpy.data.objects.new("Rib", rme)
        copy.matrix_world = ob.matrix_world
        scene.collection.objects.link(copy)
        mesh=rme

        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(mesh.polygons[858].normal * 10 ))

        bm.clear()  # interesting without.
        bpy.ops.object.select_all(action='DESELECT')
        copy.select_set(True)
        for child in copy.children:
            child.select_set(True)
        bpy.ops.object.delete()

bpy.ops.screen.animation_play()

for i in range( len( bpy.app.handlers.frame_change_pre ) ):
    bpy.app.handlers.frame_change_pre.pop()

bpy.app.handlers.frame_change_pre.append(my_handler)