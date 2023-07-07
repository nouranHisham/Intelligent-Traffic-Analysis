def hamming(state1, state2):
  return sum(map(str.__ne__, state1, state2))

def firstRewardFunction(action, observation):
    try:
        reward = 0
        waitingTime = observation[0]

        if waitingTime == 0:
            reward = reward + 1
        elif (waitingTime / 10) < 0.2:
            reward = reward - 0.5
        elif (waitingTime / 10) > 0.5:
            reward = reward - 1

        reward = reward + 0.1 * action.count("g") - 0.1 * action.count("r")

        return reward
    except:
        return 0

def secondRewardFunction(action, observation, last_action):
    try:
        reward = 0
        occupancy = observation[1]
        haltingCars = observation[2]
        emergencyStops = observation[4]

        trafficFlow = occupancy / haltingCars

        if (last_action is None):
            return 0
        
        reward = reward + trafficFlow - hamming(last_action, action) - emergencyStops

        return  reward
    except:
        return 0
