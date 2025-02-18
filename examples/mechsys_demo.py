import asyncio
import numpy as np
from mechsys_uav import UAV
import haversine

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

async def fly_to_position(uav, goal_position, relative_altitude=2.0, horizontal_uncertainity=1.0):
    # Fly to position
    accepted = await uav.send_goal_position(goal_position[0], goal_position[1], relative_altitude)
    
    # Wait for UAV to reach position
    while accepted:
        await asyncio.sleep(0.1)
        current_position = uav.get_position()
        distance = get_abs_distance(current_position, goal_position)
        print(f"Current distance: {distance:.2f} m")
        if distance <= horizontal_uncertainity:
            print("Reached position.")
            break

async def fly_to_relative_position(uav, rel_position_x, rel_position_y=0.0, relative_altitude=2.0, horizontal_uncertainity=0.2):
    current_position = uav.get_position()
    current_heading_deg = uav.get_attitude()[2]

    goal_distance = np.sqrt(np.square(rel_position_x) + np.square(rel_position_y))
    goal_heading_rad = np.arctan2(rel_position_y, rel_position_x) + (current_heading_deg / 180) * np.pi

    # Calculate goal position
    goal_position = haversine.inverse_haversine(point=current_position[0:2], distance=goal_distance, direction=goal_heading_rad, unit=haversine.Unit.METERS)
    # Fly to position
    accepted = await uav.send_goal_position(goal_position[0], goal_position[1], relative_altitude, current_heading_deg)
    # Wait for UAV to reach position
    while accepted:
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
    flight_altitude = 2.0
    horizontal_uncertainity = 0.2
    veritcal_uncertainity = 0.2

    # Wait for connection
    await asyncio.sleep(2)

    # Print initial position and attitude
    print("Initial position:", uav.get_position())
    
    # Takeoff to 2.0 m altitude
    await takeoff(uav, takeoff_altitude=flight_altitude, vertical_uncertainity=veritcal_uncertainity)
    
    # Hover for 2 seconds
    await asyncio.sleep(2)

    # Set center distance
    center_dist = 2.0
    # Fly to positions around center distance
    print(f"\nFlying to x=-{center_dist}, y=-{center_dist}")
    await fly_to_relative_position(uav=uav, rel_position_x=-center_dist, rel_position_y=-center_dist, relative_altitude=flight_altitude, 
                                   horizontal_uncertainity=horizontal_uncertainity)
    await asyncio.sleep(5)

    print(f"\nFlying to x={2*center_dist}, y=0.0")
    await fly_to_relative_position(uav=uav, rel_position_x=2*center_dist, rel_position_y=0.0, relative_altitude=flight_altitude, 
                                   horizontal_uncertainity=horizontal_uncertainity)
    await asyncio.sleep(5)

    print(f"\nFlying to x=0.0, y={2*center_dist}")
    await fly_to_relative_position(uav=uav, rel_position_x=0.0, rel_position_y=2*center_dist, relative_altitude=flight_altitude, 
                                   horizontal_uncertainity=horizontal_uncertainity)
    await asyncio.sleep(5)

    print(f"\nFlying to x=-{2*center_dist}, y=0.0")
    await fly_to_relative_position(uav=uav, rel_position_x=-2*center_dist, rel_position_y=0.0, relative_altitude=flight_altitude, 
                                   horizontal_uncertainity=horizontal_uncertainity)
    await asyncio.sleep(5)

    print(f"\nFlying to x=0.0, y=-{2*center_dist}")
    await fly_to_relative_position(uav=uav, rel_position_x=0.0, rel_position_y=-2*center_dist, relative_altitude=flight_altitude, 
                                   horizontal_uncertainity=horizontal_uncertainity)
    await asyncio.sleep(5)

    print(f"\nFlying to x={center_dist}, y={center_dist}")
    await fly_to_relative_position(uav=uav, rel_position_x=center_dist, rel_position_y=center_dist, relative_altitude=flight_altitude, 
                                   horizontal_uncertainity=horizontal_uncertainity)
    
    # Hover for 2 seconds
    await asyncio.sleep(2)

    # Land the UAV
    await uav.land()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
