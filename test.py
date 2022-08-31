import blenderproc as bproc
import numpy as np
import bpy
from bpy.props import BoolProperty

bproc.init()

obj= bproc.loader.load_blend("/homeL/9munir/Blender_cloth/BlueShirt_halfHung.blend")

# Create a point light next to it
light = bproc.types.Light()
light.set_location([2, -2, 0])
light.set_energy(300)

print('line14')
# Set the camera to be in front of the object
cam_pose = bproc.math.build_transformation_mat([4.6, -8.5, 8.69], [np.pi / 2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

#print(list(bpy.data.objects))
#print('start baking')
#bpy.ops.nla.bake(frame_start=10, frame_end=300, bake_types={'OBJECT'})
#bpy.ops.screen.animation_play(reverse=True, sync=True)


class SimpleOperator(bpy.types.Operator):
    '''Play n Stop'''
    bl_idname = "anim.simple_operator"
    bl_label = "Simple Anim Operator"
    

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        #begin from particular frame
        scene.frame_set(55)
        #play the animation
        bpy.ops.screen.animation_play()
        #if frame in particular position, stop it

        return {'FINISHED'}

def unregister():
    bpy.utils.unregister_class(SimpleOperator)



def stop_anim(scene):
    if scene.frame_current == scene["end"]:  # &gt;=  may be better.
        print("cancel")
        bpy.ops.screen.animation_cancel(restore_frame=scene.restore_frame)


def init_scene_props():
    scene = bpy.context.scene
    
    #lazy quick id props.
    scene["start"] = 10
    scene["end"] = 100
    
    #bool prop to get checkbox 
    bpy.types.Scene.restore_frame = BoolProperty(default=False)
    scene.restore_frame = True
    
    bpy.app.handlers.frame_change_pre.append(stop_anim)
    
    
init_scene_props()   
bpy.utils.register_class(SimpleOperator)
    
#obj[4].enable_rigidbody(active=True)
#obj[2].enable_rigidbody(active=False, collision_shape="MESH")

#bproc.object.simulate_physics_and_fix_final_poses(min_simulation_time=10, max_simulation_time=300, check_object_interval=1)

bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_normals_output()
bproc.renderer.set_noise_threshold(0.01)  # this is the default value

# Render the scene
data = bproc.renderer.render()


# Write the rendering into an hdf5 file
bproc.writer.write_hdf5("output/", data)
