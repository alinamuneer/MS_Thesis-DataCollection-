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
from scipy.spatial.transform import Rotation as R

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
origional_cloth_location=bpy.data.objects['Cloth_2'].location[1] #-0.06533010303974152


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
    grasp_area_location_array = [tmp_obj.data.polygons[6487],tmp_obj.data.polygons[5734],tmp_obj.data.polygons[6485],tmp_obj.data.polygons[5733],tmp_obj.data.polygons[6488],tmp_obj.data.polygons[5709],tmp_obj.data.polygons[5743],tmp_obj.data.polygons[5742],tmp_obj.data.polygons[5710]]
    sum=tmp_obj.data.polygons[6487].center
    for polygon in grasp_area_location_array[1:]:
        sum=polygon.center+sum
    OGP_vertex_location_vector=sum/len(grasp_area_location_array)
    OGP_vertex_location_vector= np.array([OGP_vertex_location_vector[0],OGP_vertex_location_vector[1],OGP_vertex_location_vector[2]])
    grasp_area_face_normal_array = [tmp_obj.data.polygons[6487],tmp_obj.data.polygons[5734],tmp_obj.data.polygons[6485],tmp_obj.data.polygons[5733],tmp_obj.data.polygons[6488],tmp_obj.data.polygons[5709],tmp_obj.data.polygons[5743],tmp_obj.data.polygons[5742],tmp_obj.data.polygons[5710]]
    sum=tmp_obj.data.polygons[6487].normal
    for polygon in grasp_area_face_normal_array[1:]:
        sum=polygon.normal+sum
    OGP_face_normal_vector=sum/len(grasp_area_face_normal_array)
    face_normal =  np.array([OGP_face_normal_vector[0],OGP_face_normal_vector[1], OGP_face_normal_vector[2]])
    cloth_mesh_drop_direction=(grasp_mesh.vertices[5931].co - grasp_mesh.vertices[5929].co) + (grasp_mesh.vertices[5989].co - grasp_mesh.vertices[5960].co) / 2
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
    rotation_step=0.1
    rounds=5
    #limit rotation rounds of euler2
    rounds_euler2=2
    #when euler1 is rotated, some up and down movements for the objects need to be done for realistic grasp of gripper and hanger
    location_step_euler1=0.08
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,100,10):
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
                    for energy in np.arange(0.2,0.9,0.3):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        print(origional_movement_count_first,origional_movement_count_second,origional_movement_count_third,origional_movement_count_fourth,origional_movement_count_fifth,origional_movement_count_sixth)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection-REDfirst/'+ '-origional'+'rotation'+str(origional_movement_count_first)+str(origional_movement_count_second)+str(origional_movement_count_third)+str(origional_movement_count_fourth)+str(origional_movement_count_fifth)+str(origional_movement_count_sixth)+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite('./DataCollection-REDfirst/'+ '-Origional'+'rotation'+str(origional_movement_count_first)+str(origional_movement_count_second)+str(origional_movement_count_third)+str(origional_movement_count_fourth)+str(origional_movement_count_fifth)+str(origional_movement_count_sixth)+'-frame'+str(frames) + '-energy'+str(energy)+ob.name +'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #saved quarternions are x y z w
                        r = R.from_matrix([[ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0]],[OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1]],[OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2]]])
                        quarternion_array=r.as_quat()
                        rows = ['-Origional'+'rotation'+str(origional_movement_count_first)+str(origional_movement_count_second)+str(origional_movement_count_third)+str(origional_movement_count_fourth)+str(origional_movement_count_fifth)+str(origional_movement_count_sixth)+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', quarternion_array[0], quarternion_array[1], quarternion_array[2],quarternion_array[3],OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]]
                        with open('./DataCollection-REDfirst/OGP_dataset_collection_RED.csv', 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(rows)
                        #bpy.ops.mesh.primitive_cube_add(size=0.1, location=(OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]))



        bpy.context.scene.frame_set(0)
        if origional_movement_count_first==rounds_euler2+1 :
            if origional_movement_count_second==rounds_euler2+1:
                if origional_movement_count_third==rounds+1:
                    if origional_movement_count_fourth==rounds+1:
                        if origional_movement_count_fifth==rounds+1:

                            if origional_movement_count_sixth<rounds:
                                #change the front
                                bpy.data.objects['Cloth_2'].rotation_euler[0]+=rotation_step
                                bpy.data.objects['hanger_Collision'].rotation_euler[0]+=rotation_step
                                bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=rotation_step
                                origional_movement_count_sixth+=1
                                run_and_stop_animation_rotation_origional()
                            if origional_movement_count_sixth==rounds:
                                bpy.data.objects['Cloth_2'].rotation_euler[0]+=-(rotation_step*rounds)
                                bpy.data.objects['hanger_Collision'].rotation_euler[0]+=-(rotation_step*rounds)
                                bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=-(rotation_step*rounds)
                                origional_movement_count_sixth+=1

                        if origional_movement_count_fifth<rounds:
                            #change the back
                            bpy.data.objects['Cloth_2'].rotation_euler[0]+=-rotation_step
                            bpy.data.objects['hanger_Collision'].rotation_euler[0]+=-rotation_step
                            bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=-rotation_step
                            origional_movement_count_fifth+=1
                            run_and_stop_animation_rotation_origional()
                        if origional_movement_count_fifth==rounds:
                            bpy.data.objects['Cloth_2'].rotation_euler[0]+=(rotation_step*rounds)
                            bpy.data.objects['hanger_Collision'].rotation_euler[0]+=(rotation_step*rounds)
                            bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=(rotation_step*rounds)
                            origional_movement_count_fifth+=1

                    if origional_movement_count_fourth<rounds:
                        #change the left
                        bpy.data.objects['Cloth_2'].rotation_euler[1]+=-rotation_step
                        bpy.data.objects['hanger_Collision'].rotation_euler[1]+=-rotation_step
                        bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=-rotation_step
                        bpy.data.objects['Cloth_2'].location[2]+=location_step_euler1
                        bpy.data.objects['hanger_Collision'].location[2]+=location_step_euler1
                        bpy.data.objects['hanger_CollisionFree'].location[2]+=location_step_euler1
                        origional_movement_count_fourth+=1
                        run_and_stop_animation_rotation_origional()
                    if origional_movement_count_fourth==rounds:
                        bpy.data.objects['Cloth_2'].rotation_euler[1]+=(rotation_step*rounds)
                        bpy.data.objects['hanger_Collision'].rotation_euler[1]+=(rotation_step*rounds)
                        bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=(rotation_step*rounds)
                        bpy.data.objects['Cloth_2'].location[2]+=-(location_step_euler1*rounds)
                        bpy.data.objects['hanger_Collision'].location[2]+=-(location_step_euler1*rounds)
                        bpy.data.objects['hanger_CollisionFree'].location[2]+=-(location_step_euler1*rounds)
                        origional_movement_count_fourth+=1

                if origional_movement_count_third<rounds:
                    #change the right
                    bpy.data.objects['Cloth_2'].rotation_euler[1]+=rotation_step
                    bpy.data.objects['hanger_Collision'].rotation_euler[1]+=rotation_step
                    bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=rotation_step
                    #bpy.data.objects['Cloth_2'].location[2]+=-location_step_euler1
                    #bpy.data.objects['hanger_Collision'].location[2]+=-location_step_euler1
                    #bpy.data.objects['hanger_CollisionFree'].location[2]+=-location_step_euler1
                    origional_movement_count_third +=1
                    run_and_stop_animation_rotation_origional()
                if origional_movement_count_third==rounds:
                    bpy.data.objects['Cloth_2'].rotation_euler[1]+=-(rotation_step*rounds)
                    bpy.data.objects['hanger_Collision'].rotation_euler[1]+=-(rotation_step*rounds)
                    bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=-(rotation_step*rounds)
                    #bpy.data.objects['Cloth_2'].location[2]+=(location_step_euler1*rounds)
                    #bpy.data.objects['hanger_Collision'].location[2]+=(location_step_euler1*rounds)
                    #bpy.data.objects['hanger_CollisionFree'].location[2]+=(location_step_euler1*rounds)
                    origional_movement_count_third +=1


            if origional_movement_count_second<rounds_euler2:
                #change the backward
                bpy.data.objects['Cloth_2'].rotation_euler[2]+=-rotation_step
                bpy.data.objects['hanger_Collision'].rotation_euler[2]+=-rotation_step
                bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=-rotation_step
                origional_movement_count_second +=1
                run_and_stop_animation_rotation_origional()
            if origional_movement_count_second==rounds_euler2:
                bpy.data.objects['Cloth_2'].rotation_euler[2]+=(rotation_step*rounds_euler2)
                bpy.data.objects['hanger_Collision'].rotation_euler[2]+=(rotation_step*rounds_euler2)
                bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=(rotation_step*rounds_euler2)
                origional_movement_count_second +=1


        if origional_movement_count_first<rounds_euler2:
            #change the forward
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=rotation_step
            bpy.data.objects['hanger_Collision'].rotation_euler[2]+=rotation_step
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=rotation_step
            origional_movement_count_first +=1
            run_and_stop_animation_rotation_origional()
        if origional_movement_count_first==rounds_euler2:
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=-(rotation_step*rounds_euler2)
            bpy.data.objects['hanger_Collision'].rotation_euler[2]+=-(rotation_step*rounds_euler2)
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=-(rotation_step*rounds_euler2)
            origional_movement_count_first=rounds_euler2+1





def run_and_stop_animation_rotation_origional():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_origional)
    return



def my_handler_rotation_forward(scene):

    global forward_rotation_count
    global origional_cloth_location
    rotation_step=0.1
    forward_location_step=0.01
    rounds=3
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,100,10):
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
                    for energy in np.arange(0.2,0.9,0.3):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection-REDfirst/'+ '-forwardRotation'+str(forward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite('./DataCollection-REDfirst/'+ '-forwardRotation'+str(forward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #saved quarternions are x y z w
                        r = R.from_matrix([[ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0]],[OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1]],[OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2]]])
                        quarternion_array=r.as_quat()
                        rows = [ '-forwardRotation'+str(forward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', quarternion_array[0], quarternion_array[1], quarternion_array[2],quarternion_array[3],OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]]
                        with open('./DataCollection-REDfirst/OGP_dataset_collection_RED.csv', 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(rows)


        bpy.context.scene.frame_set(0)
        if forward_rotation_count==rounds+1 :
            bpy.data.objects['Cloth_2'].location[1]=origional_cloth_location
            print('now start origional rotation'  )
            bpy.context.scene.frame_set(0)
            run_and_stop_animation_rotation_origional()

        if forward_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=rotation_step
            bpy.data.objects['hanger_Collision'].rotation_euler[2]+=rotation_step
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=rotation_step
            forward_rotation_count +=1
            run_and_stop_animation_rotation_forward()
        if forward_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_Collision'].rotation_euler[2]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=-(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[1]+=-forward_location_step
            if abs(bpy.data.objects['Cloth_2'].location[1] - origional_cloth_location )>=0.0001:
                forward_rotation_count=0
            else:
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
    rotation_step=0.1
    backward_location_step=0.01
    rounds=3
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,100,10):
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
                    for energy in np.arange(0.2,0.9,0.3):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection-REDfirst/'+ '-backwardRotation'+str(backward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite( './DataCollection-REDfirst/'+ '-backwardRotation'+str(backward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #saved quarternions are x y z w
                        r = R.from_matrix([[ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0]],[OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1]],[OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2]]])
                        quarternion_array=r.as_quat()
                        rows = [ '-backwardRotation'+str(backward_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', quarternion_array[0], quarternion_array[1], quarternion_array[2],quarternion_array[3],OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]]
                        with open('./DataCollection-REDfirst/OGP_dataset_collection_RED.csv', 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(rows)


        bpy.context.scene.frame_set(0)
        if backward_rotation_count==rounds+1 :
            bpy.data.objects['Cloth_2'].location[1]=origional_cloth_location
            print('now start backward rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[1]+=0.03
            run_and_stop_animation_rotation_forward()

        if backward_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=-rotation_step
            bpy.data.objects['hanger_Collision'].rotation_euler[2]+=-rotation_step
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=-rotation_step
            backward_rotation_count +=1
            run_and_stop_animation_rotation_backward()
        if backward_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[2]+=(rotation_step*rounds)
            bpy.data.objects['hanger_Collision'].rotation_euler[2]+=(rotation_step*rounds)
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[2]+=(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[1]+=-backward_location_step
            if abs(bpy.data.objects['Cloth_2'].location[1] - origional_cloth_location )>=0.0001:
                backward_rotation_count=0
            else:
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
    rotation_step=0.1
    back_location_step=0.01
    rounds=3
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,100,10):
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
                    for energy in np.arange(0.2,0.9,0.3):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection-REDfirst/'+ '-backRotation'+str(back_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite('./DataCollection-REDfirst/'+ '-backRotation'+str(back_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #saved quarternions are x y z w
                        r = R.from_matrix([[ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0]],[OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1]],[OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2]]])
                        quarternion_array=r.as_quat()
                        rows = [ '-backRotation'+str(back_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', quarternion_array[0], quarternion_array[1], quarternion_array[2],quarternion_array[3],OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]]
                        with open('./DataCollection-REDfirst/OGP_dataset_collection_RED.csv', 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(rows)


        bpy.context.scene.frame_set(0)
        if back_rotation_count==rounds+1 :
            bpy.data.objects['Cloth_2'].location[1]=origional_cloth_location
            print('now start backward rotation'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[1]+=0.03
            #this stupid backward started collisions so basically no need to slide the cloth on the hanger, simply rotate it on origional location[0]
            run_and_stop_animation_rotation_backward()


        if back_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=-rotation_step
            bpy.data.objects['hanger_Collision'].rotation_euler[0]+=-rotation_step
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=-rotation_step
            back_rotation_count +=1
            run_and_stop_animation_rotation_back()
        if back_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=(rotation_step*rounds)
            bpy.data.objects['hanger_Collision'].rotation_euler[0]+=(rotation_step*rounds)
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[1]+=-back_location_step
            if abs(bpy.data.objects['Cloth_2'].location[1] - origional_cloth_location )>=0.0001:
                back_rotation_count=0
            else:
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
    rotation_step=0.1
    front_location_step=0.01
    rounds=3
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,100,10):
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
                    for energy in np.arange(0.2,0.9,0.3):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection-REDfirst/'+ '-frontRotation'+str(front_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite('./DataCollection-REDfirst/'+ '-frontRotation'+str(front_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #saved quarternions are x y z w
                        r = R.from_matrix([[ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0]],[OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1]],[OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2]]])
                        quarternion_array=r.as_quat()
                        rows = [ '-frontRotation'+str(front_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', quarternion_array[0], quarternion_array[1], quarternion_array[2],quarternion_array[3],OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]]
                        with open('./DataCollection-REDfirst/OGP_dataset_collection_RED.csv', 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(rows)


        if front_rotation_count==rounds+1 :
            #origional_cloth_location=bpy.data.objects['Cloth_2'].location[1]
            bpy.data.objects['Cloth_2'].location[1]=origional_cloth_location
            print('now start back rotation'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[1]+=0.03
            run_and_stop_animation_rotation_back()
        bpy.context.scene.frame_set(0)
        if front_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=rotation_step
            bpy.data.objects['hanger_Collision'].rotation_euler[0]+=rotation_step
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=rotation_step
            front_rotation_count +=1
            run_and_stop_animation_rotation_front()
        if front_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[0]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_Collision'].rotation_euler[0]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[0]+=-(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[1]+=-front_location_step
            if abs(bpy.data.objects['Cloth_2'].location[1] - origional_cloth_location )>=0.0001:
                front_rotation_count=0
            else:
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
    rotation_step=0.1
    left_location_step=0.01
    rounds=3
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,100,10):
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
                    for energy in np.arange(0.2,0.9,0.3):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection-REDfirst/'+ '-leftRotation'+str(left_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite('./DataCollection-REDfirst/'+ '-leftRotation'+str(left_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #saved quarternions are x y z w
                        r = R.from_matrix([[ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0]],[OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1]],[OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2]]])
                        quarternion_array=r.as_quat()
                        rows = [ '-leftRotation'+str(left_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', quarternion_array[0], quarternion_array[1], quarternion_array[2],quarternion_array[3],OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]]
                        with open('./DataCollection-REDfirst/OGP_dataset_collection_RED.csv', 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(rows)


        bpy.context.scene.frame_set(0)
        if left_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[1]
            print('now start front rotation'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[1]+=0.03
            run_and_stop_animation_rotation_front()
        if left_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=-rotation_step
            bpy.data.objects['hanger_Collision'].rotation_euler[1]+=-rotation_step
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=-rotation_step
            left_rotation_count +=1
            run_and_stop_animation_rotation_left()
        if left_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=(rotation_step*rounds)
            bpy.data.objects['hanger_Collision'].rotation_euler[1]+=(rotation_step*rounds)
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[1]+=-left_location_step
            if abs(bpy.data.objects['Cloth_2'].location[1] - origional_cloth_location )>=0.0001:
                left_rotation_count=0
            else:
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

    rotation_step=0.1
    right_location_step=0.01
    rounds=3
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        bpy.context.view_layer.update()
        print('start rendering now')
        for frames in range(20,100,10):
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
                    for energy in np.arange(0.2,0.9,0.3):
                        bpy.data.lights['Sun'].energy=energy
                        print('energy',energy)
                        bpy.context.scene.camera = ob
                        bpy.context.scene.render.filepath = './DataCollection-REDfirst/'+ '-RightRotation'+str(Right_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name
                        bpy.ops.render.render(use_viewport=False, write_still=True)
                        dmap = get_depth()
                        cv2.imwrite('./DataCollection-REDfirst/'+ '-RightRotation'+str(Right_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', dmap * 255)
                        OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
                        #saved quarternions are x y z w
                        r = R.from_matrix([[ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0]],[OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1]],[OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2]]])
                        quarternion_array=r.as_quat()
                        rows = [ '-RightRotation'+str(Right_rotation_count*rotation_step)+'-location'+str(bpy.data.objects['Cloth_2'].location[1])+'-frame'+str(frames) + '-energy'+str(energy)+ob.name+'depth.png', quarternion_array[0], quarternion_array[1], quarternion_array[2],quarternion_array[3],OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]]
                        with open('./DataCollection-REDfirst/OGP_dataset_collection_RED.csv', 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow(rows)


        if Right_rotation_count==rounds+1 :
            origional_cloth_location=bpy.data.objects['Cloth_2'].location[1]
            print('now start left rotaion'  )
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].location[1]+=0.03
            run_and_stop_animation_rotation_left()
        bpy.context.scene.frame_set(0)
        if Right_rotation_count<rounds:
            print('changing')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=rotation_step
            bpy.data.objects['hanger_Collision'].rotation_euler[1]+=rotation_step
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=rotation_step
            Right_rotation_count +=1
            run_and_stop_animation_rotation_right()
        if Right_rotation_count==rounds:
            print('back to origionals')
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_Collision'].rotation_euler[1]+=-(rotation_step*rounds)
            bpy.data.objects['hanger_CollisionFree'].rotation_euler[1]+=-(rotation_step*rounds)
            bpy.data.objects['Cloth_2'].location[1]+=-right_location_step
            if abs(bpy.data.objects['Cloth_2'].location[1] - origional_cloth_location )>=0.0001:
                Right_rotation_count=0
            else:
                Right_rotation_count=rounds+1



        print('Right_rotation_count', Right_rotation_count)


def run_and_stop_animation_rotation_right():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler_rotation_right)
    return





print(origional_cloth_location)
print('start'+str(bpy.context.scene.frame_current)    )
bpy.context.scene.frame_set(0)
bpy.data.objects['Cloth_2'].location[1]+=0.03 #location_step*rounds
#run_and_stop_animation_rotation_origional()
run_and_stop_animation_rotation_right()
#bpy.data.objects['Cloth_2'].location[1]+=0.04
#run_and_stop_animation_rotation_front()
#run_and_stop_animation_rotation_backward()
