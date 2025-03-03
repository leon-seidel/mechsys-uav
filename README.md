# Mechsys 2025 Python API
This package includes a MAVSDK implementation for communication with a PX4 UAV or SITL simulation and offers a simple Python API that implements the following:

- Simple connection to UAV or simulation via single command
- Function calls to retrieve UAV attitude and position
- Sending goal positions with desired location, altitude and heading
- Rejection of goals outside a given flight zone and maximum altitude

The setup part of this README is required for preparing the Raspberry Pi and flight controller, while the usage part explains how to use the Mechsys Python API.

## Setup
### Install 
Install with:
```sh
pip install git+https://github.com/leon-seidel/mechsys-uav.git
```

Allow UART/USB port communication with `sudo usermod -a -G dialout $USER`. 

#### Simulation
Start SITL simulation with:
```sh
make px4_sitl gz_x500_mono_cam_baylands
```

### Flight zones
In QGroundControl build an inclusion fence and save the file to `evolonic_ros2_ws/src/mechsys/flight_zones/flight_zone.plan`.

### Raspberry Pi to flight controller connection
- UART connector
- PX4 parameter `MAV_1_CONFIG` must be set to the telem port used for the connection, usually `TELEM2`


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

## TODO:
- Check flight mode for Hold: document
- Check flight zone before takeoff
- Try UART on Pi
- 