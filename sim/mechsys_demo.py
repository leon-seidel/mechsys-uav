import asyncio
import numpy as np
from mechsys_uav import UAV
import haversine
from gz_cam import GZCamera
import detector

class PIController:
    def __init__(self, kp, ki, dt):
        self.kp = kp
        self.ki = ki
        self.dt = dt
        self.integral_x = 0.0
        self.integral_y = 0.0

    def update(self, error_x, error_y):
        # Update the integral terms
        self.integral_x += error_x * self.dt
        self.integral_y += error_y * self.dt

        # Compute the control output (setpoint) using both proportional and integral terms
        setpoint_x = self.kp * error_x + self.ki * self.integral_x
        setpoint_y = self.kp * error_y + self.ki * self.integral_y

        return setpoint_x, setpoint_y


async def run_mission(controller, uav, camera, flight_altitude):

    while True:
        # Get current position
        current_position = uav.get_position()

        # Get current frame
        frame = camera.get_latest()

        # Run detection
        _, center_position = detector.detect_red_cross(frame)
        if center_position is None:
            print("Cross not found. Hovering.")
            await asyncio.sleep(0.1)
            continue

        error_x, error_y = (center_position[0] - 160, 120 - center_position[1])
        print(f"Error: {error_x:.2f}, {error_y:.2f}")
        # Calculate error in x and y directions
        # error_x = tag_position[0] - current_position[0]
        # error_y = tag_position[1] - current_position[1]

        # Update the controller with the current errors to get the setpoints
        setpoint_x, setpoint_y = controller.update(error_y, error_x)

        # Fly to the setpoint
        await fly_to_relative_position(uav=uav, rel_position_x=setpoint_x, rel_position_y=setpoint_y, relative_altitude=flight_altitude, wait_for_arrival=False)
        await asyncio.sleep(0.1)

def get_abs_distance(position1, position2):
    return haversine.haversine(position1[0:2], position2[0:2], unit=haversine.Unit.METERS)

async def takeoff(uav, takeoff_altitude=2.0, vertical_uncertainity=0.2):
    # Arm and takeoff
    accepted = await uav.arm_and_takeoff(takeoff_altitude=takeoff_altitude)

    # Wait for UAV to reach takeoff altitude
    while accepted:
        await asyncio.sleep(0.1)
        altitude = uav.get_position()[2]
        print(f"Current altitude: {altitude:.2f} m")
        if altitude >= (takeoff_altitude - vertical_uncertainity):
            print("Reached takeoff altitude.")
            break
    return accepted


async def fly_to_relative_position(uav, rel_position_x, rel_position_y=0.0, relative_altitude=2.0, horizontal_uncertainity=0.2, wait_for_arrival=True):
    current_position = uav.get_position()
    current_heading_deg = uav.get_attitude()[2]

    goal_distance = np.sqrt(np.square(rel_position_x) + np.square(rel_position_y))
    goal_heading_rad = np.arctan2(rel_position_y, rel_position_x) + (current_heading_deg / 180) * np.pi

    # Calculate goal position
    goal_position = haversine.inverse_haversine(point=current_position[0:2], distance=goal_distance, direction=goal_heading_rad, unit=haversine.Unit.METERS)
    # Fly to position
    accepted = await uav.send_goal_position(goal_position[0], goal_position[1], relative_altitude, current_heading_deg)
    # Wait for UAV to reach position
    while accepted and wait_for_arrival:
        await asyncio.sleep(0.1)
        current_position = uav.get_position()
        distance = get_abs_distance(current_position, goal_position)
        print(f"Current distance: {distance:.2f} m")
        if distance <= horizontal_uncertainity:
            print("Reached position.")
            break

async def main():
    # Connect to UAV (simulator mode)
    uav = await UAV.connect(use_sim=True)
    camera = GZCamera()
    camera.start()

    # Create an instance of the PIController
    controller = PIController(kp=0.015, ki=0.001, dt=0.1)

    flight_altitude = 3.0
    vertical_uncertainity = 0.3

    # Wait for connection
    await asyncio.sleep(2)

    # Print initial position and attitude
    print("Initial position:", uav.get_position())
    
    # Takeoff
    while True:
        success = await takeoff(uav, takeoff_altitude=flight_altitude, vertical_uncertainity=vertical_uncertainity)
        if success:
            break
        else:
            print("Takeoff failed. Retrying...")
            await asyncio.sleep(1)

    # Hover for 2 seconds
    await asyncio.sleep(2)

    # Run the mission
    await run_mission(controller, uav, camera, flight_altitude)

    # Hover for 2 seconds
    await asyncio.sleep(2)

    # Land the UAV
    await uav.land()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
