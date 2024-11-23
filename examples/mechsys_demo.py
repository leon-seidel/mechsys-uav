# Fix needed
import asyncio
import time
from mechsys_uav.mechsys_uav import UAV

async def main():
    uav = await UAV.connect(use_sim=True)
    pos = uav.get_position()
    print(pos)
    
    # Takeoff
    goal_accepted = await uav.arm_and_takeoff(takeoff_altitude=2)

    while True:
        pos = uav.get_position()
        if pos[2] < 1.9:
            print(pos[2])
            print("Waiting for takeoff altitude")
            time.sleep(1)
        else:
            break
    
    # Fly towards goal for 5 seconds
    goal_accepted = await uav.send_goal_position(latitude=37.413240, longitude=-121.999524, relative_altitude=8, heading=11)
    time.sleep(5)

    # Land UAV
    goal_accepted = await uav.land()


# Entry point of the script
if __name__ == "__main__":
    asyncio.run(main())
