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


Right_rotation_count=0
left_rotation_count=0
front_rotation_count=0
back_rotation_count=0
forward_rotation_count=0
backward_rotation_count=0
origional_movement_count=0
origional_cloth_location=bpy.data.objects['Cloth_2'].location[0] #0.32598134875297546



def my_handler_rotation_origional(scene):
    global origional_movement_count
    global origional_cloth_location
    origional_location_step=0.1
    rounds=6
    paus=50
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(30,40,10):
            bpy.context.scene.frame_set(frames)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.6,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-origional'+'-location'+str(bpy.data.objects['Cloth_2'].location[0])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        print()
                        bpy.ops.render.render(use_viewport=False, write_still=True)


        bpy.context.scene.frame_set(0)
        if origional_movement_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            bpy.context.scene.frame_set(0)
        if origional_movement_count<rounds:
            bpy.data.objects['Cloth_2'].location[0]+=origional_location_step
            origional_movement_count +=1
            run_and_stop_animation_rotation_origional()
        if origional_movement_count==rounds:
            if bpy.data.objects['Cloth_2'].location[0] != origional_cloth_location:
                origional_movement_count=0
            elif bpy.data.objects['Cloth_2'].location[0] == origional_cloth_location:
                origional_movement_count=rounds+1





def run_and_stop_animation_rotation_origional():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_origional)
    return



def my_handler_rotation_forward(scene):

    global forward_rotation_count
    global origional_cloth_location
    rotation_step=0.2
    forward_location_step=0.2
    rounds=3
    paus=30
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,30,10):
            bpy.context.scene.frame_set(frames)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.6,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-forwardRotation'+str(forward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[0])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)



        if forward_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start origional rotation'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.6
            run_and_stop_animation_rotation_origional()
        bpy.context.scene.frame_set(0)
        if forward_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[2]+=rotation_step
            forward_rotation_count +=1
            run_and_stop_animation_rotation_forward()
        if forward_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[2]+=-(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[0]+=forward_location_step
            if bpy.data.objects['Cloth_2'].location[0] != origional_cloth_location:
                forward_rotation_count=0
            elif bpy.data.objects['Cloth_2'].location[0] == origional_cloth_location:
                forward_rotation_count=rounds+1


        print('forward_rotation_count', forward_rotation_count)




def run_and_stop_animation_rotation_forward():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_forward)
    return





def my_handler_rotation_backward(scene):

    global backward_rotation_count
    global origional_cloth_location
    rotation_step=0.2
    #backward_location_step=0.1
    rounds=3
    paus=50
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,30,10):
            bpy.context.scene.frame_set(frames)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.6,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-backwardRotation'+str(backward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[0])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)



        if backward_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start backward rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.6
            run_and_stop_animation_rotation_forward()
        bpy.context.scene.frame_set(0)
        if backward_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=-rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[2]+=-rotation_step
            backward_rotation_count +=1
            #print('vaues',bpy.data.objects['Cloth_2'].rotation_euler[2],bpy.data.objects['hanger_2'].rotation_euler[2])
            run_and_stop_animation_rotation_backward()
        if backward_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[2]+=(rotation_step*rounds)
            #bpy.data.objects['hanger_2'].rotation_euler[2]+=(rotation_step*rounds)
            #bpy.data.objects['Cloth_2'].location[0]+=backward_location_step
            if bpy.data.objects['Cloth_2'].location[0] != origional_cloth_location:
                backward_rotation_count=0
            elif bpy.data.objects['Cloth_2'].location[0] == origional_cloth_location:
                backward_rotation_count=rounds+1


        print('backward_rotation_count', backward_rotation_count)




def run_and_stop_animation_rotation_backward():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_backward)
    return



def my_handler_rotation_back(scene):

    global back_rotation_count
    global origional_cloth_location
    rotation_step=0.2
    back_location_step=0.2
    rounds=3
    paus=30
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,30,10):
            bpy.context.scene.frame_set(frames)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.6,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-backRotation'+str(back_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[0])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)



        if back_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start back rotaion'  )
            bpy.context.scene.frame_set(0)
            #this stupid backward started collisions so basically no need to slide the cloth on the hanger, simply rotate it on origional location[0]
            bpy.data.objects['Cloth_2'].location[0]=origional_cloth_location
            run_and_stop_animation_rotation_backward()
        bpy.context.scene.frame_set(0)
        if back_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=-rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[0]+=-rotation_step
            back_rotation_count +=1
            run_and_stop_animation_rotation_back()
        if back_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[0]+=(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[0]+=back_location_step
            if bpy.data.objects['Cloth_2'].location[0] != origional_cloth_location:
                back_rotation_count=0
            elif bpy.data.objects['Cloth_2'].location[0] == origional_cloth_location:
                back_rotation_count=rounds+1


        print('back_rotation_count', back_rotation_count)




def run_and_stop_animation_rotation_back():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_back)
    return


def my_handler_rotation_front(scene):

    global front_rotation_count
    global origional_cloth_location
    rotation_step=0.2
    front_location_step=0.2
    rounds=3
    paus=30
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,30,10):
            bpy.context.scene.frame_set(frames)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.6,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-frontRotation'+str(front_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[0])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)



        if front_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start back rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.6
            run_and_stop_animation_rotation_back()
        bpy.context.scene.frame_set(0)
        if front_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[0]+=rotation_step
            front_rotation_count +=1
            run_and_stop_animation_rotation_front()
        if front_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[0]+=-(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[0]+=front_location_step
            if bpy.data.objects['Cloth_2'].location[0] != origional_cloth_location:
                front_rotation_count=0
            elif bpy.data.objects['Cloth_2'].location[0] == origional_cloth_location:
                front_rotation_count=rounds+1


        print('front_rotation_count', front_rotation_count)




def run_and_stop_animation_rotation_front():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_front)
    return



def my_handler_rotation_left(scene):
    global origional_cloth_location
    global left_rotation_count
    rotation_step=0.2
    left_location_step=0.1
    rounds=3
    paus=30
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(10,20,10):
            bpy.context.scene.frame_set(frames)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.6,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-leftRotation'+str(left_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[0])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
        if left_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start front rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.6
            run_and_stop_animation_rotation_front()
        bpy.context.scene.frame_set(0)
        if left_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=-rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[1]+=-rotation_step
            left_rotation_count +=1
            run_and_stop_animation_rotation_left()
        if left_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[1]+=(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[0]+=left_location_step
            if bpy.data.objects['Cloth_2'].location[0] != origional_cloth_location:
                left_rotation_count=0
            elif bpy.data.objects['Cloth_2'].location[0] == origional_cloth_location:
                left_rotation_count=rounds+1


        print('left_rotation_count', left_rotation_count)



def run_and_stop_animation_rotation_left():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_left)
    return





def my_handler_rotation_right(scene):

    global Right_rotation_count
    global origional_cloth_location
    rotation_step=0.2
    right_location_step=0.2
    rounds=3
    paus=30
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,30,10):
            bpy.context.scene.frame_set(frames)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.6,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-RightRotation'+str(Right_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[0])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)



        if Right_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start left rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.3
            run_and_stop_animation_rotation_left()
        bpy.context.scene.frame_set(0)
        if Right_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[1]+=rotation_step
            Right_rotation_count +=1
            run_and_stop_animation_rotation_right()
        if Right_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[1]+=-(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[0]+=right_location_step
            if bpy.data.objects['Cloth_2'].location[0] != origional_cloth_location:
                Right_rotation_count=0
            elif bpy.data.objects['Cloth_2'].location[0] == origional_cloth_location:
                Right_rotation_count=rounds+1



        print('Right_rotation_count', Right_rotation_count)




def run_and_stop_animation_rotation_right():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_right)
    return







print('start'+str(bpy.context.scene.frame_current)    )
bpy.context.scene.frame_set(0)
bpy.data.objects['Cloth_2'].location[0]+=-0.6 #location_step*rounds
#run_and_stop_animation_rotation_origional()
run_and_stop_animation_rotation_right()
#run_and_stop_animation_rotation_backward()
