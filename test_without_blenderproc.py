import bpy
from bpy.props import BoolProperty
import numpy as np
import time

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 300
#bpy.ops.screen.frame_jump(end=True)


def my_handler(scene):
    paus=100
    if bpy.context.scene.frame_current ==paus-1:
        bpy.ops.screen.animation_cancel()
        bpy.context.scene.frame_current = paus

        bpy.context.view_layer.update()
        get_OGP()

#if bpy.ops.scene.frame_current == 100:
    #bpy.ops.screen.animation_cancel(restore_frame=False)


def get_OGP():
    cloth_object = bpy.data.objects['Cloth']
    #cloth_object = cloth_object_.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')

    OGP_vertex_location_vector= (cloth_object.data.vertices[214].co + cloth_object.data.vertices[1035].co + cloth_object.data.vertices[1046].co + cloth_object.data.vertices[1991].co ) / 4ob.
    OGP_vertex_location_vector= np.array([OGP_vertex_location_vector[0],OGP_vertex_location_vector[1],OGP_vertex_location_vector[2]])

    #getting matrix of the object
    cloth_transform_matrix_world = cloth_object.matrix_world

    #gripper_approach direction of the face
    gripper_approach_direction=(cloth_object.data.vertices[214].co - cloth_object.data.vertices[1035].co) + (cloth_object.data.vertices[1046].co - cloth_object.data.vertices[1991].co) / 2
    gripper_approach_direction.normalize()
    gripper_approach_direction =  np.array([gripper_approach_direction[0],gripper_approach_direction[1], gripper_approach_direction[2]])

    #face normal, indicates bi_normal direction of the gripper
    face_normal = cloth_object.data.polygons[858].normal
    face_normal =  np.array([face_normal[0],face_normal[1], face_normal[2]])

    #to get the third vector, which is the normal of the gripper, cross product the gripper_approach direction and face_normal
    third_vector = np.cross(face_normal, gripper_approach_direction)

    #convert OGP_vertex_location_vector, face_normal, gripper_approach_direction, third_vector into np.array 4x4 and store into OGP_vertex_local
    OGP_transform_matrix_local= np.array([[third_vector[0],face_normal[0],gripper_approach_direction[0],OGP_vertex_location_vector[0]],
                                    [third_vector[1],face_normal[1],gripper_approach_direction[1],OGP_vertex_location_vector[1]],
                                    [third_vector[2],face_normal[2],gripper_approach_direction[2],OGP_vertex_location_vector[2]],
                                    [0,0,0,1]])

    #transforming Optimal Grasping Point vertex position from local to world coordinates
    OGP_vertex_global = np.matmul(np.array(cloth_transform_matrix_world), OGP_transform_matrix_local)
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(OGP_vertex_global[0][3], OGP_vertex_global[1][3], OGP_vertex_global[2][3]))


bpy.ops.screen.animation_play()

for i in range( len( bpy.app.handlers.frame_change_pre ) ):
    bpy.app.handlers.frame_change_pre.pop()

bpy.app.handlers.frame_change_pre.append(my_handler)

#bpy.app.handlers.frame_change_post.append()







# class SimpleOperator(bpy.types.Operator):
#     '''Play n Stop'''
#     bl_idname = "anim.simple_operator"
#     bl_label = "Simple Anim Operator"
#
#
#     @classmethod
#     def poll(cls, context):
#         return True
#
#     def execute(self, context):
#         scene = context.scene
#         #begin from particular frame
#         scene.frame_set(10)
#         #play the animation
#         bpy.ops.screen.animation_play()
#         #if frame in particular position, stop it
#
#         return {'FINISHED'}
#
# def unregister():
#     bpy.utils.unregister_class(SimpleOperator)
#
#
# def stop_anim(scene):
#     if scene.frame_current == scene["end"]:  # &gt;=  may be better.
#         print("cancel")
#         bpy.ops.screen.animation_cancel(restore_frame=scene.restore_frame)
#
#
# def init_scene_props():
#     scene = bpy.context.scene
#
#     #lazy quick id props.
#     scene["start"] = 10
#     scene["end"] = 100
#
#     #bool prop to get checkbox
#     bpy.types.Scene.restore_frame = BoolProperty(default=False)
#     scene.restore_frame = True
#
#     bpy.app.handlers.frame_change_pre.append(stop_anim)
#
#
# init_scene_props()
# bpy.utils.register_class(SimpleOperator)
