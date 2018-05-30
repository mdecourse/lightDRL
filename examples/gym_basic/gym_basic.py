# Run with DDPG
#   python ../../server.py
#   python gym_basic.py DDPG.yaml
#   
# Author:  kbehouse  <https://github.com/kbehouse/>
#          

import sys, os
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'../../'))
from client import Client, EnvSpace
import gym
import time
from config import cfg, get_yaml_name
import numpy as np

TRAIN_MODE = True
MAX_EPISODES = 1000
RENDER = True

ENV_NAME = 'CartPole-v0' 

class GymBasic(EnvSpace):
    def env_init(self):
        self.env = gym.make(ENV_NAME)
        self.state = self.env.reset()
        self.send_state_get_action(self.state)

    def on_predict_response(self, action):
        # self.var = self.var * 0.9995 if self.ep_use_step > cfg['DDPG']['memory_capacity'] else self.var
        # a = np.clip(np.random.normal(action, self.var), *self.env.action_bound) 
        next_state, reward, done, _ = self.env.step(action)
        # print(next_state)
        self.send_train_get_action(self.state, action, reward , done, next_state)
        self.state = next_state
    
        # print('self.env_name=',self.env_name)
        if self.ep>=2 and RENDER:
            self.env.render()   
        if done:
            self.state =  self.env.reset()
            self.send_state_get_action(self.state)

def modify_cfg():
    env = gym.make(ENV_NAME)
    # env.seed(1)     # reproducible, general Policy gradient has high variance
    env = env.unwrapped
    # print('type(env.action_space.n) = ' + str(type(env.action_space)))
    # print(env.action_space.n)
    # print(env.action_space)
    # print(env.observation_space.shape)
    # print(env.observation_space.high)
    # print(env.observation_space.low)
    cfg['RL']['action_num'] = env.action_space.n
    cfg['RL']['action_discrete'] = True if type(env.action_space) == gym.spaces.discrete.Discrete else False
    cfg['RL']['state_shape'] = env.observation_space.shape
    env.close()
    return cfg

if __name__ == '__main__':
    c = Client(GymBasic, project_name='gym-'+ ENV_NAME + '-' + get_yaml_name(), i_cfg = modify_cfg(), retrain_model= True)
