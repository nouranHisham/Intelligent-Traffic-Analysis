from sumoEnv import SumoEnv
from agent import Agent, FullDqnAgent
from rewardfn import firstRewardFunction, secondRewardFunction
import pandas as pd
import ast
import argparse
import json
from theParser import parse

cmd = argparse.ArgumentParser()
arguments = parse(cmd)

max_steps = arguments.i

cl = 'clusters_maxabs_3dimensions'

traffic_light_counts_to_include =  [1 ,2 ,3 ,4]
scenario = arguments.s

use_full_dqn = arguments.fulldqn

if arguments.re == "1":
    reward_function = firstRewardFunction 
else:
    reward_function = secondRewardFunction

gui = "-gui"

class config():
    def __init__(self, sumoBinary, sumoCmd, sumo_home=None):
        self.sumoBinary = sumoBinary
        self.sumoCmd = sumoCmd
        self.sumo_home = sumo_home



df = None
if scenario == "lust":
    lust_file_name = "./datasets/dataset-lust-tl-clusters.csv"
    path = "D:/Intelligent-Traffic-Analysis/LuSTScenario-master/LuSTScenario-master/scenario/due.static.sumocfg"
    lust_raw_df = pd.read_csv(lust_file_name)
    lust_raw_df['trafficlight_count'] = lust_raw_df['trafficlight_count'].map(lambda x: ast.literal_eval(x))
    df = lust_raw_df
else:
    path = "D:/Traffic-Management-System-CCE/Alex/osm.sumocfg"
    cgn_file_name = "./datasets/dataset-alex-tl-clusters.csv"
    cgn_raw_df = pd.read_csv(cgn_file_name)
    cgn_raw_df['trafficlight_count'] = cgn_raw_df['trafficlight_count'].map(lambda x: ast.literal_eval(x))
    df = cgn_raw_df
    
WinPythonPortableConfigGui = config(
    "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe",
    ["C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe", "-c",
     path],
    "C:/Program Files (x86)/Eclipse/Sumo"
)

df['tl_counts'] = df['trafficlight_count'].map(lambda x: x[0])

clusters = []
for tl_count in traffic_light_counts_to_include:
    filtered_df = df[df['tl_counts'] == tl_count]
    g = filtered_df.groupby(filtered_df[cl])
    for name, group in g:
        tl_ids = group['trafficlight_count'].map(lambda x: x[1])
        clusters.append((name, list(tl_ids), tl_count))

filtered_df = df[df['tl_counts'].isin(traffic_light_counts_to_include)]
traffic_lights = list(map(lambda x: (x[0], x[1]), filtered_df["trafficlight_count"]))


env = SumoEnv(WinPythonPortableConfigGui, traffic_lights, reward_function)

agent_infos = []
for (cluster_id, tl_ids, count) in clusters:

    stateCnt = env.stateCnt(tl_ids[0])
    actionCnt = env.actionCnt(tl_ids[0])
    iniStates = []
    for i in range(len(tl_ids)):
        iniStates.append(env.emptyState(tl_ids[0]))
    if use_full_dqn:
        new_agent = FullDqnAgent(stateCnt, actionCnt)
    else:
        new_agent = Agent(stateCnt, actionCnt)
    agent_infos.append(
        [
            new_agent,
            tl_ids,
            iniStates,
            None
        ]
    )

brainFileName = "scen_{}_sizes_{}_cluster_{}_iterations_{}_sumo_brain.h5".format(scenario,
                                                                                 traffic_light_counts_to_include, cl,
                                                                                 max_steps)
rewardFileName = "scen_{}_sizes_{}_cluster_{}_iterations_{}_sumo_rewards.json".format(scenario,
                                                                                      traffic_light_counts_to_include,
                                                                                      cl, max_steps)
rewards = []

steps = 0
R = 0

while True:
    for agent_info in agent_infos:
        agent = agent_info[0]
        tl_id_list = agent_info[1]
        state_list = agent_info[2]
        action_list = []
        
        for i, tl_id in enumerate(tl_id_list):
            print(state_list)
            action = agent.act(state_list[i])
            env.setAction(action, tl_id)
            action_list.append(action)

        agent_info[3] = action_list

    steps += 1

    env.step()

    for agent_info in agent_infos:
        agent = agent_info[0]
        tl_id_list = agent_info[1]
        state_list = agent_info[2]
        action_list = agent_info[3]
        new_state_list = []
        for i, tl_id in enumerate(tl_id_list):
            s = state_list[i]
            a = action_list[i]
            s_, r, done, info = env.actionResults(tl_id)
            rewards.append(r)
            agent.observe((s, a, r, s_))
            agent.replay()
            new_state_list.append(s_)
        agent_info[2] = new_state_list

    if done:  
        s_ = None

    if steps == max_steps:
        env.close()
        agent.brain.model.save(brainFileName)
        f = open(rewardFileName, 'w')
        json.dump(rewards, f)
        f.close()
        break

    if done:
        break


