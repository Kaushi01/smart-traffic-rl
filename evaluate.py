import sumo_rl
from stable_baselines3 import DQN

env = sumo_rl.SumoEnvironment(
    net_file="cross.net.xml",
    route_file="cross.rou.xml",
    out_csv_name="outputs/eval",
    use_gui=False,
    num_seconds=1200,
    delta_time=5,
    yellow_time=3,
    min_green=5,
    max_green=40,
    single_agent=True,
    additional_sumo_cmd="--tripinfo-output tripinfo_rl.xml --no-warnings",
)

model = DQN.load("dqn_traffic")
obs, info = env.reset()
done = False
while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
env.close()
print("Evaluation done")