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

context = bpy.context
scene = context.scene
cloth_object = bpy.data.objects['Cloth_2']
bpy.context.scene.frame_set(30)
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
            bpy.context.scene.render.filepath = './DataCollection-RED/'+'-energy'+str(energy)+ob.name
            bpy.ops.render.render(use_viewport=False, write_still=True)
            OGP_transform_matrix_camera=np.matmul(np.linalg.inv(bpy.data.objects[ob.name].matrix_world),OGP_transform_matrix_global)
            bpy.ops.mesh.primitive_cube_add(size=0.005, location=(OGP_transform_matrix_camera[0][3], OGP_transform_matrix_camera[1][3], OGP_transform_matrix_camera[2][3]))
            #print(OGP_transform_matrix_global)
            print(OGP_transform_matrix_camera)







            #bpy.ops.mesh.primitive_cube_add(size=0.1, location=(OGP_transform_matrix_global[0][3], OGP_transform_matrix_global[1][3], OGP_transform_matrix_global[2][3]))
