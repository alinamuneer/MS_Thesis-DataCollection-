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
origional_movement_count_first=0
origional_movement_count_second=0
origional_movement_count_third=0
origional_movement_count_fourth=0
origional_movement_count_fifth=0
origional_movement_count_sixth=0
origional_cloth_location=bpy.data.objects['Cloth_2'].location[0] #0.32598134875297546

def transform_obj_to_frame(layer, ground):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = ground.evaluated_get(depsgraph)
    tmpMesh = bpy.data.meshes.new_from_object(object_eval)
    tmpMesh.transform(ground.matrix_world)
    tmp_ground = bpy.data.objects.new(name='tmpGround', object_data=tmpMesh)
    layer.active_layer_collection.collection.objects.link(tmp_ground)
    layer.update()
    return tmp_ground


def get_OGP(tmp_obj):
    grasp_mesh = tmp_obj.data
    grasp_area_location_array = [tmp_obj.data.polygons[3187],tmp_obj.data.polygons[3162],tmp_obj.data.polygons[875],tmp_obj.data.polygons[850],tmp_obj.data.polygons[872],tmp_obj.data.polygons[849],tmp_obj.data.polygons[3184]]
    sum=tmp_obj.data.polygons[3187].center
    for polygon in grasp_area_location_array[1:]:
        sum=polygon.center+sum
    OGP_vertex_location_vector=sum/len(grasp_area_location_array)
    OGP_vertex_location_vector= np.array([OGP_vertex_location_vector[0],OGP_vertex_location_vector[1],OGP_vertex_location_vector[2]])
    grasp_area_face_normal_array = [tmp_obj.data.polygons[3187],tmp_obj.data.polygons[3162],tmp_obj.data.polygons[875],tmp_obj.data.polygons[850],tmp_obj.data.polygons[872],tmp_obj.data.polygons[849],tmp_obj.data.polygons[3184],tmp_obj.data.polygons[3161],tmp_obj.data.polygons[2313],tmp_obj.data.polygons[5],tmp_obj.data.polygons[1],tmp_obj.data.polygons[2317],tmp_obj.data.polygons[4],tmp_obj.data.polygons[2],tmp_obj.data.polygons[2314],tmp_obj.data.polygons[2316]]
    sum=tmp_obj.data.polygons[3187].normal
    for polygon in grasp_area_face_normal_array[1:]:
        sum=polygon.normal+sum
    OGP_face_normal_vector=sum/len(grasp_area_face_normal_array)
    face_normal =  np.array([OGP_face_normal_vector[0],OGP_face_normal_vector[1], OGP_face_normal_vector[2]])
    cloth_mesh_drop_direction=(grasp_mesh.vertices[583].co - grasp_mesh.vertices[578].co) + (grasp_mesh.vertices[1035].co - grasp_mesh.vertices[1034].co) / 2
    cloth_mesh_drop_direction.normalize()
    gripper_approach_direction = np.cross(face_normal, cloth_mesh_drop_direction)
    third_vector = np.cross(face_normal, gripper_approach_direction)
    OGP_transform_matrix_global= np.array([[third_vector[0],face_normal[0],gripper_approach_direction[0],OGP_vertex_location_vector[0]],
                                        [third_vector[1],face_normal[1],gripper_approach_direction[1],OGP_vertex_location_vector[1]],
                                        [third_vector[2],face_normal[2],gripper_approach_direction[2],OGP_vertex_location_vector[2]],                                  [0,0,0,1]])
    #print(OGP_transform_matrix_global)
    #bpy.ops.mesh.primitive_cube_add(size=0.1, location=(OGP_transform_matrix_local[0][3], OGP_transform_matrix_local[1][3], OGP_transform_matrix_local[2][3]))
    return OGP_transform_matrix_global


def get_depth():
    z = bpy.data.images['Viewer Node']
    w, h = z.size
    dmap = np.array(z.pixels[:], dtype=np.uint16) # convert to numpy array
    dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
    dmap = np.rot90(dmap, k=2)
    dmap = np.fliplr(dmap)
    return dmap



def my_handler_rotation_origional(scene):
    global origional_movement_count_first
    global origional_movement_count_second
    global origional_movement_count_third
    global origional_movement_count_fourth
    global origional_movement_count_fifth
    global origional_movement_count_sixth
    global origional_cloth_location
    rotation_step=0.2
    rounds=3
    paus=30
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(30,40,10):
            context = bpy.context
            scene = context.scene
            cloth_object = bpy.data.objects['Cloth_2']
            bpy.context.scene.frame_set(frames)
            layer = bpy.context.view_layer
            tmp_obj = transform_obj_to_frame(layer, cloth_object)
            OGP_transform_matrix_global=get_OGP(tmp_obj)
            bpy.data.objects.remove(bpy.data.objects['tmpGround'], do_unlink=True)
            for ob in bpy.context.scene.objects:
                if ob.type == 'CAMERA':
                    for energy in np.arange(0.2,0.3,0.2):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection/'+ '-origional'+'rotation'+str(origional_movement_count_first)+str(origional_movement_count_second)+str(origional_movement_count_third)+str(origional_movement_count_fourth)+str(origional_movement_count_fifth)+str(origional_movement_count_sixth)+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite('./DataCollection/'+ '-origional'+'rotation'+str(origional_movement_count_first)+str(origional_movement_count_second)+str(origional_movement_count_third)+str(origional_movement_count_fourth)+str(origional_movement_count_fifth)+str(origional_movement_count_sixth)+'-frame'+str(frames) + '-energy'+str(energy)+ob.name +'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #print(OGP_transform_matrix_camera)
                        rows = {
                            'name': [ 'Image'+'-origional'+'rotation'+str(origional_movement_count_first)+str(origional_movement_count_second)+str(origional_movement_count_third)+str(origional_movement_count_fourth)+str(origional_movement_count_fifth)+str(origional_movement_count_sixth)+'-frame'+str(frames) + '-energy'+str(energy)+ob.name, '', '',''],
                            'Binormal': [ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0],OGP_transform_matrix_camera[3][0]],
                            'Normal': [OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1],OGP_transform_matrix_camera[3][1]],
                            'Approach': [OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2],OGP_transform_matrix_camera[3][2]],
                            'Location': [OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3],OGP_transform_matrix_camera[3][3]]}
                        df = pd.DataFrame(rows)
                        df.to_csv('./DataCollection/OGP_dataset_collection.csv', mode='a', index=False, header=False)
                        #bpy.ops.mesh.primitive_cube_add(size=0.1, location=(OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]))
                        #bpy.ops.mesh.primitive_cube_add(size=0.1, location=(OGP_transform_matrix_global[0][3], OGP_transform_matrix_global[1][3], OGP_transform_matrix_global[2][3]))


        bpy.context.scene.frame_set(0)
        if origional_movement_count_first==rounds+1 :
            if origional_movement_count_second==rounds+1:
                if origional_movement_count_third==rounds+1:
                    if origional_movement_count_fourth==rounds+1:
                        if origional_movement_count_fifth==rounds+1:

                            if origional_movement_count_sixth<rounds:
                                #change the front
                                bpy.data.objects['Cloth_2'].rotation_euler[0]+=rotation_step
                                bpy.data.objects['hanger_2'].rotation_euler[0]+=rotation_step
                                origional_movement_count_sixth+=1
                                run_and_stop_animation_rotation_origional()
                            if origional_movement_count_sixth==rounds:
                                bpy.data.objects['Cloth_2'].rotation_euler[0]+=-(rotation_step*rounds)
                                bpy.data.objects['hanger_2'].rotation_euler[0]+=-(rotation_step*rounds)
                                origional_movement_count_sixth+=1

                        if origional_movement_count_fifth<rounds:
                            #change the back
                            bpy.data.objects['Cloth_2'].rotation_euler[0]+=-rotation_step
                            bpy.data.objects['hanger_2'].rotation_euler[0]+=-rotation_step
                            origional_movement_count_fifth+=1
                            run_and_stop_animation_rotation_origional()
                        if origional_movement_count_fifth==rounds:
                            bpy.data.objects['Cloth_2'].rotation_euler[0]+=(rotation_step*rounds)
                            bpy.data.objects['hanger_2'].rotation_euler[0]+=(rotation_step*rounds)
                            origional_movement_count_fifth+=1

                    if origional_movement_count_fourth<rounds:
                        #change the left
                        bpy.data.objects['Cloth_2'].rotation_euler[1]+=-rotation_step
                        bpy.data.objects['hanger_2'].rotation_euler[1]+=-rotation_step
                        origional_movement_count_fourth+=1
                        run_and_stop_animation_rotation_origional()
                    if origional_movement_count_fourth==rounds:
                        bpy.data.objects['Cloth_2'].rotation_euler[1]+=(rotation_step*rounds)
                        bpy.data.objects['hanger_2'].rotation_euler[1]+=(rotation_step*rounds)
                        origional_movement_count_fourth+=1

                if origional_movement_count_third<rounds:
                    #change the right
                    bpy.data.objects['Cloth_2'].rotation_euler[1]+=rotation_step
                    bpy.data.objects['hanger_2'].rotation_euler[1]+=rotation_step
                    origional_movement_count_third +=1
                    run_and_stop_animation_rotation_origional()
                if origional_movement_count_third==rounds:
                    bpy.data.objects['Cloth_2'].rotation_euler[1]+=-(rotation_step*rounds)
                    bpy.data.objects['hanger_2'].rotation_euler[1]+=-(rotation_step*rounds)
                    origional_movement_count_third +=1


            if origional_movement_count_second<rounds:
                #change the backward
                bpy.data.objects['Cloth_2'].rotation_euler[2]+=-rotation_step
                bpy.data.objects['hanger_2'].rotation_euler[2]+=-rotation_step
                origional_movement_count_second +=1
                run_and_stop_animation_rotation_origional()
            if origional_movement_count_second==rounds:
                bpy.data.objects['Cloth_2'].rotation_euler[2]+=(rotation_step*rounds)
                bpy.data.objects['hanger_2'].rotation_euler[2]+=(rotation_step*rounds)
                origional_movement_count_second +=1


        if origional_movement_count_first<rounds:
            #change the forward
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[2]+=rotation_step
            origional_movement_count_first +=1
            run_and_stop_animation_rotation_origional()
        if origional_movement_count_first==rounds:
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[2]+=-(rotation_step*rounds)
            origional_movement_count_first=rounds+1





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


        bpy.context.scene.frame_set(0)
        if forward_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start origional rotation'  )
            bpy.context.scene.frame_set(0)
            run_and_stop_animation_rotation_origional()

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


        bpy.context.scene.frame_set(0)
        if backward_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start backward rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.6
            run_and_stop_animation_rotation_forward()

        if backward_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=-rotation_step
            bpy.data.objects['hanger_2'].rotation_euler[2]+=-rotation_step
            backward_rotation_count +=1
            run_and_stop_animation_rotation_backward()
        if backward_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=(rotation_step*rounds)
            bpy.data.objects['hanger_2'].rotation_euler[2]+=(rotation_step*rounds)
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


        bpy.context.scene.frame_set(0)
        if back_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start back rotaion'  )
            bpy.context.scene.frame_set(0)
            #this stupid backward started collisions so basically no need to slide the cloth on the hanger, simply rotate it on origional location[0]
            bpy.data.objects['Cloth_2'].location[0]=origional_cloth_location
            run_and_stop_animation_rotation_backward()


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


        bpy.context.scene.frame_set(0)
        if front_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start back rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.6
            run_and_stop_animation_rotation_back()
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

        bpy.context.scene.frame_set(0)
        if left_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[0]
            print('now start front rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[0]+=-0.6
            run_and_stop_animation_rotation_front()
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
