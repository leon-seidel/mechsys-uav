# Mechsys 2026 Python API
This package includes a MAVSDK implementation for communication with a PX4 UAV or SITL simulation and offers a simple Python API that implements the following:

- Simple connection to UAV or simulation via single command
- Function calls to retrieve UAV attitude and position
- Sending goal positions with desired location, altitude and heading
- Rejection of goals outside a given flight zone and maximum altitude
- Only allow sending commands to the drone when the flight mode is "Hold"

The setup part of this README is required for preparing the Raspberry Pi and flight controller, while the usage part explains how to use the Mechsys Python API.

## System setup

Use Ubuntu 22.04 or 24.04 and then install Git, Curl and uv if not already available:
```sh
sudo apt update
sudo apt install git curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install PX4 SITL with the following commands

```sh
git clone https://github.com/PX4/PX4-Autopilot.git --branch v1.16.1 --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
```

Then follow the tutorial [here](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html#ubuntu) to install the latest stable release of QGroundControl.

## Setup
### Install 
Create a project that uses `mechsys-uav` as a dependency:
```sh
mkdir my-uav-project
cd my-uav-project
uv init --bare
uv venv
source .venv/bin/activate
uv add git+https://github.com/leon-seidel/mechsys-uav.git
```

If you are adding `mechsys-uav` to an existing uv project, run `uv add` from the directory that already contains `pyproject.toml`.

#### Simulation
Start SITL simulation with:
```sh
cd ~/PX4-Autopilot/
make px4_sitl gz_x500_mono_cam_baylands
```

### Raspberry Pi to flight controller connection
Enable serial port UART communication on the Pi with raspi-config: Go to Interface Options -> Serial Port and select the following before rebooting:

Would you like a login shell to be accessible over the serial? - No

Would you like the serial port hardware to be enabled? - Yes

Build a connector from TELEM2 on the flight controller to UART ports on the Raspberry Pi, connecting RX->TX, TX->RX and Ground. Allow UART port communication with `sudo usermod -a -G dialout $USER`. The PX4 parameter `MAV_1_CONFIG` must be set to the serial port used for the connection, like `GPS1` and the baud rate (e.g. `SER_GPS1_BAUD`) to 57600 8N1.

## Usage
Connect with the following with the `use_sim` flag or a `serial_port` and `serial_baud`. It is also possible to set another UDP port for the simulation.
The flight zone is automatically set for simulation (Gazebo baylands) and real world testing, other plans can be loaded with `flight_zone_name`.
```py
from mechsys_uav import UAV
uav = await UAV.connect(use_sim=True)
```

Run your scripts from that project with `uv run`, for example `uv run python your_script.py`.

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
from mechsys_uav import UAV
uav = await UAV.connect(use_sim=True, udp_port=14541)
```
## Drone and image coordinate systems
Image coordinate systems usually start in the top left corner of the image, while the drone coordinate system in a bottom down image lies in the center of the image. The x and y directions are also different as visualised here:
![coordinate_systems](https://github.com/user-attachments/assets/0cef72b8-ed53-49f7-a8aa-3ef62f089e24)

## Flight zones (only for custom flight zones)
In QGroundControl build an inclusion fence and save the file to `mechsys_uav/flight_zones/flight_zone.plan`.

# vl53l8cx driver
## portable files
- Core/Inc/vl53l8cx/ — all API / plugin / buffer headers
- Core/Src/vl53l8cx/vl53l8cx_api.c, vl53l8cx.c, and the plugin .c files — these are platform-independent sensor logic

## must be rewritten for RPi
- vl53l8cx_platform.h
- vl53l8cx_platform.c
- main.c — only here for reference: power-on sequence, I2C address `0x52`, etc.

## VL53L8CX good to knows

### Power-on sequence
1. Pull **PWREN** and **LPn** both LOW → wait 100 ms  (clears any hung sensor state)
2. Set **PWREN** HIGH → wait 50 ms
3. Set **LPn** HIGH → wait **250 ms** (critical: sensor internal boot)

### I2C
- Address: `0x52` (8-bit)
- 16-bit register addressing (`I2C_MEMADD_SIZE_16BIT`)

### Sensor configuration
| Parameter | Value |
|-----------|-------|
| Resolution | 8×8 (64 zones) |
| Ranging frequency | 10 Hz |

### Output data (per frame)
Each frame contains 64 zones, one entry per zone:
- `distance_mm` — distance in mm
- `signal_per_spad` — signal strength (uint32)
- `target_status` — validity flag (5 = valid)

## GPIO pins (STM32 reference — remap for RPi)
<img width="595" height="953" alt="image" src="https://github.com/user-attachments/assets/c4f3f5c3-ae32-4021-9b31-404f009389a3" />



