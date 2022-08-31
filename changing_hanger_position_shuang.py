import bmesh
import bpy
from bpy.props import BoolProperty
import numpy as np
import time
from math import radians
import os
import csv
import cv2
import pandas as pd

flag=False
count=0

def transform_obj_to_frame(layer, ground):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = ground.evaluated_get(depsgraph)
    tmpMesh = bpy.data.meshes.new_from_object(object_eval)
    tmpMesh.transform(ground.matrix_world)
    tmp_ground = bpy.data.objects.new(name='tmpGround', object_data=tmpMesh)
    layer.active_layer_collection.collection.objects.link(tmp_ground)
    layer.update()
    return


def my_handler(scene):
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        bpy.context.scene.frame_set(0)
    return

def run_and_stop_animation():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler)
    return

def continue_():
    global count
    if count==0:
        print(count)
        bpy.context.scene.frame_set(0)
        bpy.data.objects['Cloth_2'].rotation_euler[1]+=-0.7
        bpy.data.objects['hanger_2'].rotation_euler[1]+=-0.7
        count=1
        run_animation()
        bpy.context.scene.frame_set(0)
        print('updated count',count)


    elif count==1:
        print(count)
        bpy.context.scene.frame_set(0)
        bpy.data.objects['Cloth_2'].rotation_euler[1]+=0.2
        bpy.data.objects['hanger_2'].rotation_euler[1]+=0.2

def my_handler_rotation(scene):

    print(bpy.context.scene.frame_current)
    current_frame=50
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        #print('handler'+str(bpy.context.scene.frame_current)    )
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        bpy.context.scene.frame_set(current_frame)
        print('start rendering now')
        for ob in bpy.context.scene.objects:
            if ob.type == 'CAMERA':
                bpy.context.scene.camera = ob
                bpy.context.scene.render.filepath = './DataCollection/'+ '-afterRotation' +str(count)+ ob.name
                bpy.ops.render.render(use_viewport=False, write_still=True)
        print('here')
        continue_()




def run_animation():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()



# for ob in bpy.context.scene.objects:
#     if ob.type == 'CAMERA':
#         bpy.context.scene.camera = ob
#         bpy.context.scene.render.filepath = './DataCollection/'+ '-Outside' + ob.name
#         bpy.ops.render.render(use_viewport=False, write_still=True)
#


print('start'+str(bpy.context.scene.frame_current)    )

bpy.context.scene.frame_set(0)
bpy.data.objects['Cloth_2'].rotation_euler[1]+=0.5
bpy.data.objects['hanger_2'].rotation_euler[1]+=0.5
run_animation()
bpy.app.handlers.frame_change_post.append(my_handler_rotation)





#run_and_stop_animation()
#run_and_stop_animation_right()


#bpy.data.objects.remove(bpy.data.objects['Cloth_2'], do_unlink=True)


#bpy.context.scene.frame_set(0)
#bpy.data.objects['tmpGround'].rotation_euler[1]+=-0.2
#bpy.data.objects['hanger_2'].rotation_euler[1]+=-0.2
