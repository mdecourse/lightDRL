
from fetch_cam.fetch_discrete import FetchDiscreteEnv, EnvType
from fetch_cam.img_process import ImgProcess, IMG_TYPE, IMG_SHOW, MergeImage
import cv2
import numpy as np
import os

# because thread bloack the image catch (maybe), so create the shell class 
class FetchDiscreteCamEnv:
    def __init__(self, dis_tolerance = 0.001, step_ds=0.005, img_type = IMG_TYPE.RGB, 
                    env_type = EnvType.RedCube, is_render = False, only_show_obj0=False, 
                    img_show_type = IMG_SHOW.RAW_PROCESS):
        self.env = FetchDiscreteEnv(dis_tolerance = 0.001, step_ds=0.005, env_type=env_type, is_render = is_render)
        self.img_type = img_type
        self.is_render = is_render
        self.only_show_obj0 = only_show_obj0

        self.imp = ImgProcess(img_type, flip=True)
        self.imp.show_type = img_show_type

        if self.is_render:
            self.merge_img = MergeImage(height = 600, width = 600)

    

    def step(self,action):
        # print('i action = ', action)
        if self.is_render:
            self.merge_img.show_arrow(action)
        a_one_hot = np.zeros(6)
        a_one_hot[action] = 1
        s, r, d, _ = self.env.step(a_one_hot)

        # no use, but you need preserve it; otherwise, you will get error image
        rgb_external = self.env.sim.render(width=256, height=256, camera_name="external_camera_0", depth=False,
                    mode='offscreen', device_id=-1)
        rgb_gripper = self.env.sim.render(width=256, height=256, camera_name="gripper_camera_rgb", depth=False,
            mode='offscreen', device_id=-1)
        
        rgb_gripper =  cv2.cvtColor(rgb_gripper, cv2.COLOR_BGR2RGB)
        process_img = self.imp.preprocess(rgb_gripper)
        # RESIZE
        # resize_img = cv2.resize(process_img, (IMG_W_H, IMG_W_H), interpolation=cv2.INTER_AREA)

        if self.is_render:
            # show merge
            show_process = process_img*255 if self.img_type == IMG_TYPE.SEMANTIC else process_img

            self.merge_img.merge(rgb_gripper, rgb_external, rgb_gripper, show_process)
            self.merge_img.save_2_video()
            self.merge_img.show()

        return process_img, r, d, cv2.cvtColor(rgb_gripper, cv2.COLOR_BGR2RGB)


    @property
    def pos(self):
        return self.env.pos

    @property
    def obj_pos(self):
        return self.env.obj_pos

    @property
    def red_tray_pos(self):
        return self.env.red_tray_pos

    @property
    def gripper_state(self):
        return self.env.gripper_state

    @property
    def is_gripper_close(self):
        return self.env.is_gripper_close

    def reset(self):
        # self.env.rand_objs_color(exclude_obj0 = True)
        # self.env.rand_red_or_not(obj_name='object0', use_red_color=True)
        self.env.rand_red_or_not(obj_name='object1', use_red_color=False)
        self.env.rand_red_or_not(obj_name='object2', use_red_color=False)
        self.env.reset()
        if self.only_show_obj0:
            self.env.hide_obj1_obj2()
        self.env.render()
        rgb_external = self.env.sim.render(width=256, height=256, camera_name="external_camera_0", depth=False,
                    mode='offscreen', device_id=-1)
        rgb_gripper = self.env.sim.render(width=256, height=256, camera_name="gripper_camera_rgb", depth=False,
            mode='offscreen', device_id=-1)
    
        rgb_gripper =  cv2.cvtColor(rgb_gripper, cv2.COLOR_BGR2RGB)
        process_img = self.imp.preprocess(rgb_gripper)

        if self.is_render:
            # show merge
            show_process = process_img*255 if self.img_type == IMG_TYPE.SEMANTIC else process_img

            self.merge_img.merge(rgb_gripper, rgb_external, rgb_gripper, show_process)
            self.merge_img.save_2_video()
            self.merge_img.show()

        return process_img

    def render(self):
        self.env.render()
