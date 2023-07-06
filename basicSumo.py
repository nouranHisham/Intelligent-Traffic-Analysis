from sumo_environment import SumoEnv
import sys
import argparse



parser = argparse.ArgumentParser(description='Run a traci controlled sumo simulation running reinforcement learning.')
parser.add_argument('-i', type=int, help='how many iterations/simulation steps to execute', default=30000)
parser.add_argument('-s', help='which scenario to run. possible values are: {cgn|lust}', default="cgn")




args = parser.parse_args()
max_num_steps=args.i
scenario=args.s
gui=""

print("Running simulation({} steps) scenario '{}' for trafficlight counts{}: and clustering result: {}".format(max_num_steps,scenario, "[None]", "None"))
sys.stdout.flush()

class config():
    def __init__(self, sumoBinary, sumoCmd, sumo_home=None):
        self.sumoBinary = sumoBinary
        self.sumoCmd = sumoCmd
        self.sumo_home = sumo_home


LinuxConfig = config(
    "/usr/bin/sumo{}".format(gui),
    None
 )
if scenario=="lust":
    LinuxConfig.sumoCmd=["/usr/bin/sumo{}".format(gui), "-c", "/home/ganjalf/sumo/LuSTScenario/scenario/dua.static.sumocfg"]
else:
    LinuxConfig.sumoCmd =["/usr/bin/sumo{}".format(gui), "-c", "/home/ganjalf/sumo/TAPASCologne-0.24.0/cologne.sumocfg"]


WinPythonPortableConfig = config(
    "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo.exe",
    ["C:/Program Files (x86)/Eclipse/Sumo/bin/sumo.exe", "-c", 'D:\Traffic-Management-System-CCE\LuSTScenario-master\LuSTScenario-master\scenario\lust.net.xml'],
    "C:/Program Files (x86)/Eclipse/Sumo"
)

WinPythonPortableConfigGui = config(
    "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe",
    ["C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe", "-c", './Alex/osm.sumocfg'],
    "C:/Program Files (x86)/Eclipse/Sumo"
)

#env = SumoEnv(LinuxConfig, [], lambda x: x)
env = SumoEnv(WinPythonPortableConfigGui, [], lambda x: x)



for i in range(max_num_steps):
    env.simulationStepOnly()

env.close()

print("Ran simulation scenario '{}' for trafficlight counts{}: and clustering result: {}".format(scenario, "[None]", "None"))

print("reward function used:{}".format("none"))