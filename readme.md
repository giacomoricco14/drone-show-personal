# 🚁 CrazySim & CrazySwarm2 with Gazebo

Simulate single or multiple drones in ROS 2 and Gazebo.
*Ref: "Setup CrazySim e CrazySwarm2 con Gazebo.pdf"*

---

## 📦 1. Install & Clone 

Start the docker container and reach the `ros2_ws/src` folder.
Clone the following repository (with submodules) and install dependencies:

```bash
git clone https://github.com/gtfactslab/CrazySim.git --recursive
pip install Jinja2
```

## 🏗️ 2. Build Firmware (SITL)

Compile the low-level firmware:

```bash
cd crazyflie-firmware
mkdir -p sitl_make/build && cd $_
cmake ..
make all
cd ../..
```

## 🚀 3. Run Simulator (Gazebo)

Once you have done the previous steps (that can be done once and for all), you can proceed with the following instructions.
Choose between single or multiple agents. *(Drones listen on `udp://127.0.0.1:19850`, port increments per drone).*

**🎯 Single Agent:**
```bash
bash tools/crazyflie-simulation/simulator_files/gazebo/launch/sitl_singleagent.sh -m crazyflie -x 0 -y 0
```

**🐝 Multi-Agent (e.g., 8 drones):**
```bash
bash tools/crazyflie-simulation/simulator_files/gazebo/launch/sitl_multiagent_square.sh -n 8 -m crazyflie
```

## ⚙️ 4. Build CrazySwarm2

Compile the ROS 2 workspace:

```bash
cd crazyswarm2_ws
pip3 install "setuptools<80.0.0"
rm -r build/ install/ log/
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

## 🏁 5. Configure & Launch

### 📝 Configuration
File: `crazyswarm2_ws/src/crazyswarm2/crazyflie/config/crazyflies.yaml`
- `enabled: true` 👉 Active agents in simulator (e.g., `cf_1`, `cf_2`)
- `enabled: false` 👉 Unused agents

### 🟢 Launch Services
Start the server using the default C++ backend:

```bash
ros2 launch crazyflie launch.py backend:=cpp
```

---

## 🕹️ 6. Run a node to make your drone fly

Let's assume you have used a single drone by considering the `sitl_singleagent.sh` and a `crazyflies.yaml` where only one drone is active, you can decide to make your drone fly with the python files in the `crazyflie_examples` folder.
You can open another terminal and run the following command: 

```bash
ros2 run crazyflie_examples hello_world
```

This file will simply make your nanoquadcopter take off and land.

Similarly, with a multiple drones configuration you can start the flight of the first drone with the same command or use the following to make them all take off:

```bash
ros2 run crazyflie_examples nice_hover
```

---

## 💻 7. Cfclient Interface

Another way to start your drones is by using the user interface.
This is a simple way to connect and start your drones both in simulation and reality.
First install the software inside the container with the commands:

```bash
pip3 install cfclient
apt-get update && apt-get install -y libxcb-cursor0 libxcb-xinerama0 libxcb-shape0 libxkbcommon-x11-0
```
 
Then simply run it with:

```bash
cfclient
```

---

## 🎮 8. Simulation with Gazebo

We will make extensive use of simulation. 
We need to run the virtual firmware in Gazebo and connect to it using the ROS 2 server.

**Step 1:** Open a terminal and go to the `crazyflie-firmware` folder. Start Gazebo and the SITL firmware:
```bash
bash tools/crazyflie-simulation/simulator_files/gazebo/launch/sitl_singleagent.sh -m crazyflie -x 0 -y 0
```
*(Note: This step is only for simulation and must not be performed during experimentation with real hardware).*

**Step 2:** Open a **second terminal** and launch the C++ ROS 2 server using the simulation configuration file (which contains the UDP addresses):
```bash
cd src/crazyswarm2/crazyflie/config
ros2 launch crazyflie launch.py backend:=cpp crazyflies_yaml_file:=crazyflies_sim.yaml gui:=False
```
*(Ensure that `crazyflies_sim.yaml` has the correct `udp://127.0.0.1:1985X` addresses and that `kalman: resetEstimation: 1` is **commented out**).*

**Step 3:** Finally, open a **third terminal** and execute your flight script:
```bash
ros2 run crazyflie_examples hello_world
```

---

## 🌍 9. Real Experiment

Now we will make use of the configuration file which is named `crazyflies.yaml`.
Give a look at this file to make sure that everything is at right place. In particular make sure that:

*   ✅ The right number of drones is active (`enabled: true`).
*   ✅ The positioning system is correctly configured (e.g., `loco.mode: 1` for TWR).
*   ✅ The data rate in the URI matches your cfclient configuration (e.g., `radio://0/100/2M/...` or `1M` or`250K`).
*   ✅ The Kalman filter for position estimation is ON (the reset is **uncommented** in the `all: -> firmware_params:` section: `kalman: resetEstimation: 1`).

**Step 1:** Open a terminal and run the ROS 2 server:
```bash
ros2 launch crazyflie launch.py
```

**Step 2:** Open another terminal and make your drone fly:
```bash
ros2 run crazyflie_examples hello_world
```
