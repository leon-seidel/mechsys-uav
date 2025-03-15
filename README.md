# Mechsys 2025 Python API
This package includes a MAVSDK implementation for communication with a PX4 UAV or SITL simulation and offers a simple Python API that implements the following:

- Simple connection to UAV or simulation via single command
- Function calls to retrieve UAV attitude and position
- Sending goal positions with desired location, altitude and heading
- Rejection of goals outside a given flight zone and maximum altitude
- Only allow sending commands to the drone when the flight mode is "Hold"

The setup part of this README is required for preparing the Raspberry Pi and flight controller, while the usage part explains how to use the Mechsys Python API.

## System setup
In Ubuntu 22.04 install PX4 SITL with the following commands:

```sh
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
```

Then follow the tutorial [here](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html#ubuntu) to install QGroundControl.

## Setup
### Install 
Install with:
```sh
pip install git+https://github.com/leon-seidel/mechsys-uav.git
```

#### Simulation
Start SITL simulation with:
```sh
cd ~/PX4-Autopilot/
make px4_sitl gz_x500_mono_cam_baylands
```

### Raspberry Pi to flight controller connection
Build a connector from TELEM2 on the flight controller to UART ports on the Raspberry Pi, connecting RX->TX, TX->RX and Ground. Allow UART port communication with `sudo usermod -a -G dialout $USER`. The PX4 parameter `MAV_1_CONFIG` must be set to the telem port used for the connection, like `TELEM2`

## Usage
Connect with the following with the `use_sim` flag or a `serial_port` and `serial_baud`:
```py
from uav_node_mavsdk import UAV
uav = await UAV.connect(use_sim=True)
```

You can then query the UAV's attitude in degrees:
```py
uav.pitch, uav.roll, uav.heading
```

You can also query the position coordinates and relative altitude above takeoff/home position in m:
```py
uav.latitude, uav.longitude, uav.relative_altitude
```

To arm and takeoff the UAV to a given relative takeoff altitude use:
```py
goal_accepted = await uav.arm_and_takeoff(takeoff_altitude=2)
```

To send a goal position to the UAV specify a latitude, longitude and relative altitude above takeoff/home position in m: 
```py
goal_accepted = await uav.send_goal_position(latitude=37.413240, longitude=-121.999524, relative_altitude=8)
```

This will return `True` if the goal was accepted before sending a command to the UAV, in case of goal rejection `False` is returned. To add a heading in degrees to the flight path do the following:
```py
goal_accepted = await uav.send_goal_position(latitude=37.413240, longitude=-121.999524, relative_altitude=8, heading=11)
```
The heading is used directly, which means that the UAV first turns to the desired heading and then proceeds to the goal position or altitude keeping the heading.

To land the UAV use:
```py
goal_accepted = await uav.land()
```

## Gazebo camera
The `examples/gz_cam.py` script can be used to interface with the Gazebo camera's simulator. You can use it with:
```py
from gz_cam import GZCamera
cam = GZCamera(show_image=True) # Setting show_image to True starts a live view window
cam.start()                     # Starting the camera feed

cam.get_latest()                # Get the latest camera frame
```

## Add rover to simulation
To get the rover with the red cross replace the contents of `~/PX4-Autopilot/Tools/simulation/gz/models/r1_rover` with the files in `examples/r1_rover`.

Then go to the PX4 folder and launch the copter simulation in the first terminal.
```sh
cd ~/PX4-Autopilot/
make px4_sitl

PX4_GZ_MODEL_POSE="0,-2" PX4_GZ_WORLD=baylands PX4_SIM_MODEL=gz_x500_mono_cam_down ./build/px4_sitl_default/bin/px4 -i 1
```

Wait until Gazebo is launched and start a second terminal for the rover:

```sh
cd ~/PX4-Autopilot/
PX4_GZ_WORLD=baylands  PX4_SIM_MODEL=gz_r1_rover ./build/px4_sitl_default/bin/px4 -i 2
```

As the drone's UDP port changes slightly with a second vehicle set it to Port 14541 when connecting:
```py
from uav_node_mavsdk import UAV
uav = await UAV.connect(use_sim=True, port=14541)
```

### Flight zones (only for custom flight zones)
In QGroundControl build an inclusion fence and save the file to `mechsys_uav/flight_zones/flight_zone.plan`.
