from __future__ import division
import sys
import os
import itertools
import os
import numpy as np
import csv

try:
    import traci
except ImportError:
    if "SUMO_HOME" in os.environ:
        sys.path.append(
            os.path.join(os.environ["SUMO_HOME"], "tools")
        )
        import traci
    else:
        raise EnvironmentError("Importing Traci failed or SUMO was not found in the system")

class Agent_Info(object):
    pass


class SumoEnv():

    def actionCount(self,tl_id):
        agent = self.agent_data[tl_id]
        return len (list(self.action_spaces[agent.tl_count]))

    def stateCount(self,tl_id):
        return 5

    def __init__(self, config, traffic_light_info,reward_function):
        self.action_spaces = [None] * 12  
        self.edges = []
        self.agent_data = {}
        self.lanes = []
        self.reward_function=reward_function
        self.config = config
        self.startTraci()
        self.current_step=0

        for (count, tl_id) in (traffic_light_info):
            info = Agent_Info()
            info.tl_count = count
            info.tl_id = tl_id
            info.vehicles_last_step={}
            info.last_action=None
            info.lanes= traci.trafficlight.getControlledLanes(tl_id)
            info.edges = self.getSumoEdgeInformationFromTraci(tl_id)
            self.intializeActionSpace(count)
            self.agent_data[tl_id] = info

    def getSumoEdgeInformationFromTraci(self, tl_id):
        lanes = traci.trafficlight.getControlledLanes(tl_id)
        result = []
        for lane in lanes:
            result.append(traci.lane.getEdgeID(lane))
        return result

    def intializeActionSpace(self, size):
        if self.action_spaces[size] is not None:
            return
        space = map(''.join, itertools.product("rgyGu", repeat=size))
        self.action_spaces[size] = list(space)

    def actionResults(self, tl_id):
        agent_info= self.agent_data[tl_id]
        return agent_info.observation, agent_info.reward, False, {}

    def simulationStepOnly(self):
        traci.simulationStep()

    def simulationStepNoObservations(self):
        self.performActions()
        traci.simulationStep()

    def step(self):
        self.performActions()
        traci.simulationStep()
        self.current_step+=1
        self.makeObservations()
        self.computeRewards()
        self.storeLastActions()

    def storeLastActions(self):
        for tl_id, agent in self.agent_data.items():
            action_space= self.action_spaces[agent.tl_count]
            agent.last_action=action_space[agent.action]

    def computeRewards(self):
         for tl_id, agent in self.agent_data.items():
            action = self.action_spaces[agent.tl_count][agent.action]
            agent.reward= self.reward_function(action, agent.observation, agent.last_action)

    def makeObservations(self):
        for tl_id, agent in self.agent_data.items():
            agent.observation = self.getSensors(agent.tl_id)

    def performActions(self):
        for tl_id, agent in self.agent_data.items():
            action_space= self.action_spaces[agent.tl_count]
            action_space = list(action_space)
            traci.trafficlight.setRedYellowGreenState(tl_id, action_space[agent.action])

    def setAction(self, action, tl_id):
        self.agent_data[tl_id].action=action

    def getSensors(self,tl_id):
        edges=self.agent_data[tl_id].edges
        vehicles_started_to_teleport = traci.simulation.getStartingTeleportNumber()
        lanes = self.agent_data[tl_id].lanes
        vehicles_last_step = self.agent_data[tl_id].vehicles_last_step
        emergency_stops=0
        vehicles={}

        for lane in lanes:
            ids= traci.lane.getLastStepVehicleIDs(lane)
            for id in ids:
                speed= traci.vehicle.getSpeed(id)
                vehicles[id]=speed
                if id in vehicles_last_step:
                    if vehicles_last_step[id]-speed>4.5:
                        emergency_stops+=1
        self.agent_data[tl_id].vehicles_last_step=vehicles

        observation = []
        for e_id in edges:
            edge_values = [traci.edge.getLastStepOccupancy(e_id), traci.edge.getLastStepVehicleNumber(e_id), traci.edge.getLastStepHaltingNumber(e_id)]
            observation.append(edge_values)

        observation = np.matrix(observation).mean(0).tolist()[0]

        observation.append(vehicles_started_to_teleport)
        observation.append(emergency_stops)

        return np.array(observation)

    def close(self):
        traci.close()

    def startTraci(self):
        if self.config.sumo_home is not None:
            os.environ["SUMO_HOME"] = self.config.sumo_home
        if "-gui" in self.config.sumoCmd[0]:
            self.gui=True
        else:
            self.gui=False
        traci.start(self.config.sumoCmd)

    def emptyState(self, tl_id):
        return np.zeros(self.stateCount(tl_id))