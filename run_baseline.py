import traci

traci.start(["sumo", "-c", "cross.sumocfg"])

total_waiting = 0
steps = 0
cars_seen = set()

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    for car in traci.vehicle.getIDList():
        total_waiting += traci.vehicle.getWaitingTime(car)
        cars_seen.add(car)
    steps += 1

traci.close()
print("Steps run:", steps)
print("Cars seen:", len(cars_seen))
print("Total waiting time:", total_waiting)
print("Average waiting per car:", total_waiting / max(len(cars_seen), 1))