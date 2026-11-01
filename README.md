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

## How to run

### 1. Install (once)

```bash
sudo apt install -y ros-jazzy-desktop ros-jazzy-ros-gz \
  ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-simulations ros-jazzy-turtlebot3-navigation2 \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox ros-jazzy-sros2 \
  python3-colcon-common-extensions python3-rosdep git

echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
```

### 2. Build the workspace

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

### 3. Start exploration

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
