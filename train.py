import sumo_rl
from stable_baselines3 import DQN

env = sumo_rl.SumoEnvironment(
    net_file="cross.net.xml",
    route_file="cross.rou.xml",
    out_csv_name="outputs/dqn",
    use_gui=False,
    num_seconds=1200,
    delta_time=5,
    yellow_time=3,
    min_green=5,
    max_green=40,
    single_agent=True,
)

model = DQN(
    "MlpPolicy",
    env,
    learning_rate=0.001,
    buffer_size=50000,
    learning_starts=100,
    exploration_fraction=0.3,
    verbose=1,
)

model.learn(total_timesteps=20000)
model.save("dqn_traffic")
print("Training done")