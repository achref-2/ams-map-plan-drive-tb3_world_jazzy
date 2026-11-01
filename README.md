# mpd_bringup: Simulation and autonomous mapping (baseline)

Part of the project **Secure Autonomous Exploration and Mapping with ROS 2**, for *Special Aspects of Mobile Autonomous Systems* (TH Köln, WS 26/27).

This package is **Person 1's part (M1)**: a TurtleBot3 in Gazebo explores an unknown environment on its own and builds a map with slam_toolbox, Nav2 and explore_lite. It is the **baseline and test platform** for the team. Our own frontier-exploration node and the SROS2 security layer build on it.

**Author:** Achraf Aroua
**Versions:** Ubuntu 24.04 · ROS 2 Jazzy · Gazebo Harmonic · TurtleBot3 Burger

---

## What it does

One launch file starts the whole stack:

```
Gazebo (TurtleBot3) ──/scan,/odom──▶ slam_toolbox ──/map──▶ explore_lite ──goal──▶ Nav2 ──/cmd_vel──▶ robot
                                                         └──/explore/frontiers──▶ RViz2
```

- **Gazebo Harmonic** simulates the TurtleBot3 Burger with its 360° laser scanner.
- **slam_toolbox** builds the occupancy-grid map and localizes the robot (SLAM).
- **explore_lite** finds frontiers (edges between known and unknown space) and sends the next one to Nav2 as a goal.
- **Nav2** plans a path and drives the robot there.
- **RViz2** shows the SLAM map, laser scan, global costmap, planned path, robot model and frontiers (`rviz/exploration.rviz`).

## Results

**Turtle world, mapped autonomously on ROS 2 Jazzy:** outer hexagon walls and all 9 pillars, clean map (`maps/tb3_world_jazzy`).

![Turtle world map on Jazzy](docs/04_turtle_world_jazzy.png)

**First large map of the TurtleBot3 house** (earlier run on ROS 2 Humble). Green spheres are open frontiers.

![House map](docs/02_house_map.png)

## Environment setup (from zero)

Tested on **Windows 11 with WSL2**. On a native Ubuntu 24.04 PC, skip step 1.

### 1. Windows: install WSL2 with Ubuntu 24.04

In **PowerShell** (as administrator):

```powershell
wsl --install -d Ubuntu-24.04
```

Restart if Windows asks. Then open **Ubuntu 24.04** from the Start menu and create a username and password (the password is what `sudo` asks for; nothing shows while you type it).

Check that it runs as WSL **2** and make it the default:

```powershell
wsl -l -v                         # VERSION column must say 2
wsl --set-default Ubuntu-24.04    # plain "wsl" now opens 24.04
```

Graphics (Gazebo, RViz) work through WSLg, which is built into Windows 11. Keep your Windows graphics driver up to date.

### 2. Update Ubuntu

All following commands run in the **Ubuntu 24.04** terminal:

```bash
cd ~
sudo apt update && sudo apt upgrade -y
```

### 3. Install ROS 2 Jazzy

```bash
# Language settings
sudo apt install -y locales software-properties-common curl
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
sudo add-apt-repository universe -y

# Add the ROS 2 package source
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo $VERSION_CODENAME)_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# Install ROS 2 Jazzy (a few GB, takes a while)
sudo apt update
sudo apt install -y ros-jazzy-desktop
```

If a step fails, compare with the official guide: docs.ros.org → Jazzy → Installation → Ubuntu (deb packages).

### 4. Install Gazebo Harmonic, TurtleBot3, Nav2, SLAM and SROS2

```bash
sudo apt install -y ros-jazzy-ros-gz \
  ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-simulations ros-jazzy-turtlebot3-navigation2 \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox ros-jazzy-sros2 \
  python3-colcon-common-extensions python3-rosdep git unzip
```

`ros-jazzy-ros-gz` installs **Gazebo Harmonic** and the ROS–Gazebo bridge.

### 5. Configure the terminal

```bash
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
printenv ROS_DISTRO    # should print: jazzy
```

### 6. Test the simulation

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Gazebo Harmonic should open with the TurtleBot3 in the hexagon world. In a second Ubuntu tab, drive it with the keyboard (W/A/S/D/X, S = stop):

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

Quick check that ROS graphics work: `rviz2` should open a window.

**If Gazebo stays black or crashes**, use software rendering (slower, so only if needed):

```bash
echo 'export LIBGL_ALWAYS_SOFTWARE=1' >> ~/.bashrc && source ~/.bashrc
```

### Tips for WSL

- Keep the workspace in the **Linux home folder** (`~/mpd_ws`), not under `/mnt/c/...`; the Windows drive is much slower.
- Windows files are under `/mnt/c/Users/<you>/...`, e.g. `cp /mnt/c/Users/<you>/Downloads/file.zip ~/`
- Linux files in Windows Explorer: `\\wsl$\Ubuntu-24.04\home\<you>`
- `sudo rosdep init` only works once; "already initialized" later is fine.

## How to run

### 1. Build the workspace

```bash
mkdir -p ~/mpd_ws/src && cd ~/mpd_ws/src
git clone https://github.com/achref-2/ams-map-plan-drive.git mpd_bringup
git clone https://github.com/robo-friends/m-explore-ros2.git
cd ~/mpd_ws
sudo rosdep init   # first time only
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --packages-up-to explore_lite mpd_bringup
echo 'source ~/mpd_ws/install/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

### 2. Start exploration

```bash
ros2 launch mpd_bringup exploration.launch.py
```

Gazebo and RViz open, and explore_lite starts after 20 s. When the map is complete, save it from a second terminal:

```bash
mkdir -p ~/maps && ros2 run nav2_map_server map_saver_cli -f ~/maps/tb3_world_jazzy
```

Launch options: `world:=turtlebot3_house`, `x_pose:=… y_pose:=…` (start position), `explore:=false` (no autonomous exploration; drive with teleop or click *2D Goal Pose* in RViz), `rviz:=false`.

## Configuration

All settings are **defaults**, except the two needed for the stack to start:

| File | What | Why |
|---|---|---|
| `launch/exploration.launch.py` | Gazebo, SLAM and Nav2 each in their own `GroupAction` | Gazebo's launch file sets an empty `params_file` that otherwise leaks into Nav2 and crashes it |
| `config/nav2_params.yaml` | Copy of the TurtleBot3 Jazzy Nav2 params (`turtlebot3_navigation2/param/burger.yaml`) | On Jazzy the robot expects `TwistStamped` on `/cmd_vel` (`enable_stamped_cmd_vel: true`) |
| `config/explore_params.yaml` | explore_lite defaults (`planner_frequency 0.15`, `progress_timeout 30`, `min_frontier_size 0.5`) | — |

## Known issues and findings

| Problem | Cause | Workaround |
|---|---|---|
| Build fails: `explore_lite_msgs` not found | explore_lite needs a message package from the same repo | Build with `--packages-up-to explore_lite mpd_bringup` |
| Robot stuck in a "Reached the goal" loop | explore_lite picks a frontier a few cm away; Nav2 reports it reached at once, the robot never moves, SLAM never updates | Nudge the robot once: `ros2 run turtlebot3_teleop teleop_keyboard` (W, then S) |
| Exploration stops at once in open areas | explore_lite joins frontier cells into one blob; in open space unknown cells reach the robot | Use closed environments (turtle world), or start inside a room |
| Simulation slow | Gazebo runs at about 25–30 % real time under WSL | Close other apps, minimize the Gazebo window |
| Red `Could not resolve file [Wood_Floor_Dark.jpg]` | Missing floor textures in the house world | Harmless, only visual |

**explore_lite weaknesses we found** (input for our own exploration node in M2):
1. It targets the frontier **centroid**, which can lie inside already known space.
2. It merges all frontier cells into **one connected frontier**, so frontiers touching the robot block exploration.
3. It **fails in open areas** where many laser beams hit nothing.

## Files

```
mpd_bringup/
├── launch/exploration.launch.py   # whole stack in one command
├── config/nav2_params.yaml        # TurtleBot3 Jazzy Nav2 params (TwistStamped)
├── config/explore_params.yaml     # explore_lite settings
├── rviz/exploration.rviz          # RViz2 view: map, scan, costmap, path, frontiers
├── maps/                          # saved maps (.pgm + .yaml)
└── docs/                          # screenshots for this README
```

## Next steps

- Own frontier-exploration node (M2), compared against explore_lite
- Attack scenarios and SROS2 security on top of this stack (with Person 2)
- Evaluation: exploration time, map coverage, latency and CPU load with and without security
