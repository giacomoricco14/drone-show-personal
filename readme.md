# 🚁 CrazySim & CrazySwarm2 with Gazebo

Simulate single or multiple drones in ROS2 and Gazebo.
*Ref: "Setup CrazySim e CrazySwarm2 con Gazebo.pdf"*

---

## 📦 1. Install & Clone
Clone the repo (with submodules) and install dependencies:
```bash
git clone https://github.com/gtfactslab/CrazySim.git --recursive
cd CrazySim
sudo apt update && sudo apt install cmake build-essential
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
Compile the ROS2 workspace:
```bash
cd crazyswarm2_ws
pip3 install setuptools==65.5.1
rm -rf build/ install/ log/
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

## 🏁 5. Configure & Launch

### 📝 Configuration
File: `crazyswarm2_ws/src/crazyswarm2/crazyflie/config/crazyflies.yaml`
* `enabled: true` 👉 Active agents in simulator (e.g., `cf_1`, `cf_2`)
* `enabled: false` 👉 Unused agents

### 🟢 Launch Services
Choose your backend and start:

**⚡ C++ Backend (High Performance):**
```bash
ros2 launch crazyflie launch.py backend:=cpp
```

**🐢 cflib Backend:**
```bash
ros2 launch crazyflie launch.py backend:=cflib
```
