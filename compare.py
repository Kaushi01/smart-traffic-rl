import subprocess, os
import xml.etree.ElementTree as E
import sumo_rl
from stable_baselines3 import DQN
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SUMO_HOME = os.environ["SUMO_HOME"]
RANDOM_TRIPS = os.path.join(SUMO_HOME, "tools", "randomTrips.py")

# (name, seconds between cars, seed). Smaller number = heavier traffic.
scenarios = [
    ("light-1", 3.0, 11),
    ("light-2", 3.0, 12),
    ("normal-1", 2.0, 21),
    ("normal-2", 2.0, 22),
    ("heavy-1", 1.5, 31),
    ("heavy-2", 1.5, 32),
]

def avg_wait(path):
    w = [float(t.get("waitingTime")) for t in E.parse(path).getroot()]
    return sum(w) / len(w)

model = DQN.load("dqn_traffic")
names, fixed_res, rl_res = [], [], []

for name, period, seed in scenarios:
    rou = f"test_{name}.rou.xml"
    subprocess.run(
        ["python", RANDOM_TRIPS, "-n", "cross.net.xml", "-r", rou,
         "-e", "1200", "-p", str(period), "--fringe-factor", "10",
         "--seed", str(seed)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Fixed timer
    fixed_out = f"trip_fixed_{name}.xml"
    subprocess.run(
        ["sumo", "-n", "cross.net.xml", "-r", rou, "-e", "1200",
         "--tripinfo-output", fixed_out, "--no-warnings"],
        check=True, stdout=subprocess.DEVNULL)
    f = avg_wait(fixed_out)

    # RL agent
    rl_out = f"trip_rl_{name}.xml"
    env = sumo_rl.SumoEnvironment(
        net_file="cross.net.xml", route_file=rou,
        out_csv_name="outputs/cmp", use_gui=False, num_seconds=1200,
        delta_time=5, yellow_time=3, min_green=5, max_green=40,
        single_agent=True,
        additional_sumo_cmd=f"--tripinfo-output {rl_out} --no-warnings")
    obs, info = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, r, term, trunc, info = env.step(action)
        done = term or trunc
    env.close()
    r = avg_wait(rl_out)

    names.append(name); fixed_res.append(f); rl_res.append(r)
    print(f"{name}: fixed={f:.1f}s  rl={r:.1f}s  change={(f-r)/f*100:.0f}%")

# Chart
x = range(len(names))
plt.figure(figsize=(9, 5))
plt.bar([i - 0.2 for i in x], fixed_res, width=0.4, label="Fixed timer")
plt.bar([i + 0.2 for i in x], rl_res, width=0.4, label="RL agent")
plt.xticks(list(x), names)
plt.ylabel("Average wait per car (seconds)")
plt.title("Fixed timer vs RL traffic light")
plt.legend()
plt.tight_layout()
plt.savefig("results.png", dpi=150)
print("Saved chart: results.png")