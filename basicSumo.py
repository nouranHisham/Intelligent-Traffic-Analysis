from sumo_environment import SumoEnv
import sys
import argparse



parser = argparse.ArgumentParser(description='Run a traci controlled sumo simulation running reinforcement learning.')
parser.add_argument('-i', type=int, help='how many iterations/simulation steps to execute', default=30000)
parser.add_argument('-s', help='which scenario to run. possible values are: {cgn|lust}', default="cgn")




args = parser.parse_args()
max_num_steps=args.i
scenario=args.s



class config():
    def __init__(self, sumoBinary, sumoCmd, sumo_home=None):
        self.sumoBinary = sumoBinary
        self.sumoCmd = sumoCmd
        self.sumo_home = sumo_home




SumoGUIConfig = config(
    "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe",
    ["C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe", "-c", './Alex/osm.sumocfg'],
    "C:/Program Files (x86)/Eclipse/Sumo"
)

env = SumoEnv(SumoGUIConfig, [], lambda x: x)



for i in range(max_num_steps):
    env.simulationStepOnly()

env.close()



