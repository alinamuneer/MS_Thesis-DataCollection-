#just to keep some code here
#data of cloth moved to left position

#this is 1
for desired_frame in range(40,50,10):
    for energy in np.arange(0,2.5,0.5):
         bpy.data.lights['Sun'].energy = energy
         render_and_dataCollection(desired_frame,'image-'+'frame'+str(desired_frame)+'energy'+str(energy))
bpy.context.scene.frame_set(0)
run_and_stop_animation()

#this is 2
for position in range(1,5):
    bpy.context.scene.frame_set(0)
    bpy.data.objects['Cloth_2'].location[0]+=-0.1
    run_and_stop_animation()
    for desired_frame in range(40,50,10):
        for energy in np.arange(0,2,0.5):
            bpy.data.lights['Sun'].energy = energy
            render_and_dataCollection(desired_frame,'image-'+'frame'+str(desired_frame)+'leftPosition'+str(position*0.1))
    bpy.context.scene.frame_set(0)
    for energy in np.arange(0,2,0.5):
        bpy.data.lights['Sun'].energy = energy
        render_and_rotate(20,40,position*0.1)

#this is 3
def render_and_rotate(start,stop,position,energy):
    print(bpy.data.objects['hanger_2'].rotation_euler[1])
    run_and_stop_animation()
    bpy.context.scene.frame_set(0)
    for desired_frame in range(start,stop,10):
        for i in range(1,2):
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=-0.1
            bpy.data.objects['hanger_2'].rotation_euler[1]+=-0.1
            print(str(desired_frame)+ 'frame has hanger rotation'+str(bpy.data.objects['hanger_2'].rotation_euler[1]))
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


        for i in range(1,2):
            bpy.context.scene.frame_set(0)
            bpy.data.objects['Cloth_2'].rotation_euler[1]+=0.1
            bpy.data.objects['hanger_2'].rotation_euler[1]+=0.1
            print(str(desired_frame)+ 'frame has hanger rotation'+str(bpy.data.objects['hanger_2'].rotation_euler[1]))
            run_and_stop_animation()
            bpy.context.scene.frame_set(0)
            render_and_dataCollection(desired_frame,'image-rightRotate'+str(i*0.1)+'frame'+str(desired_frame)+'ClothPosition'+str(position)+'energy'+str(energy))

        #set it back to initial
        bpy.context.scene.frame_set(0)
        bpy.data.objects['Cloth_2'].rotation_euler[1]+=-0.1
        bpy.data.objects['hanger_2'].rotation_euler[1]+=-0.1
        print(str(desired_frame)+ 'frame has hanger rotation'+str(bpy.data.objects['hanger_2'].rotation_euler[1]))
        run_and_stop_animation()
        bpy.context.scene.frame_set(0)
    return
