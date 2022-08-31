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


#testing stopping at particular frame of choice

def my_handler(scene):
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus
        context = bpy.context
        scene = context.scene
        cloth_object = bpy.data.objects['Cloth_2']
    return

def run_and_stop_animation():
    bpy.ops.screen.animation_play()
    for i in range( len( bpy.app.handlers.frame_change_pre ) ):
         bpy.app.handlers.frame_change_pre.pop()
    bpy.app.handlers.frame_change_pre.append(my_handler)
    return


def render_and_dataCollection(desired_frame,image_path):

    context = bpy.context
    scene = context.scene
    cloth_object = bpy.data.objects['Cloth_2']

    bpy.context.scene.frame_set(desired_frame)
    layer = bpy.context.view_layer
    tmp_obj = transform_obj_to_frame(layer, cloth_object)
    OGP_transform_matrix_global=get_OGP(tmp_obj)

    bpy.data.objects.remove(bpy.data.objects['tmpGround'], do_unlink=True)

    for ob in scene.objects:
         if ob.type == 'CAMERA':
             bpy.context.scene.camera = ob
             bpy.context.scene.render.filepath = './DataCollection/'+image_path + '-' + ob.name
             bpy.ops.render.render(use_viewport=False, write_still=True)
             dmap = get_depth()
             cv2.imwrite('./DataCollection/'+image_path + '-' + ob.name +'depth.png', dmap * 255)
             OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
             #print(OGP_transform_matrix_camera)
             rows = {
                 'name': [ image_path + '-' + ob.name, '', '',''],
                 'Binormal': [ OGP_transform_matrix_camera[0][0], OGP_transform_matrix_camera[1][0], OGP_transform_matrix_camera[2][0],OGP_transform_matrix_camera[3][0]],
                 'Normal': [OGP_transform_matrix_camera[0][1], OGP_transform_matrix_camera[1][1], OGP_transform_matrix_camera[2][1],OGP_transform_matrix_camera[3][1]],
                 'Approach': [OGP_transform_matrix_camera[0][2], OGP_transform_matrix_camera[1][2], OGP_transform_matrix_camera[2][2],OGP_transform_matrix_camera[3][2]],
                 'Location': [OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3],OGP_transform_matrix_camera[3][3]]
    }
             df = pd.DataFrame(rows)
             df.to_csv('./DataCollection/OGP_dataset_collection.csv', mode='a', index=False, header=False)
             #bpy.ops.mesh.primitive_cube_add(size=0.1, location=(OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]))
    return

# put 3 from temporary.py

def render_and_rotate(start,stop,position,energy):
    for desired_frame in range(start,stop,10):
        for i in range(1,2):
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=-0.1
            bpy.data.objects['hanger_2'].rotation_euler[1]+=-0.1
            run_and_stop_animation()
            bpy.context.scene.frame_set(0)
            render_and_dataCollection(desired_frame,'image-leftRotate'+str(i*0.1)+'frame'+str(desired_frame)+'ClothPosition'+str(position)+'energy'+str(energy))

        #set it back to initial
        bpy.context.scene.frame_set(0)
        bpy.data.objects['Cloth_2'].rotation_euler[1]+=0.1
        bpy.data.objects['hanger_2'].rotation_euler[1]+=0.1
        print(str(desired_frame)+ 'frame has hanger rotation'+str(bpy.data.objects['hanger_2'].rotation_euler[1]))
        run_and_stop_animation()
        bpy.context.scene.frame_set(0)




# render_and_dataCollection() collects the OGP of DESIRED FRAME, takes images of all cameras and save respective OGP for those images
bpy.context.scene.frame_set(0)
run_and_stop_animation()



#data of orginial positions in different frames for normal rendering and different frames when rotation is involved as cloth falls down
# put 1 from temporary.py

for energy in np.arange(0,1,0.2):
    bpy.data.lights['Sun'].energy = energy
    render_and_rotate(20,30,0,energy)

#put 2 from temporary.py
