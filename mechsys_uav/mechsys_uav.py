#!/usr/bin/env python3
import json
import asyncio
from importlib.resources import files
from shapely.geometry import Point, Polygon
from mavsdk import System

class UAV():
    def __init__(self):
        # Get parameters
        self._flight_zone_name = "flight_zone.plan"
        self._flight_zone_file = files("mechsys_uav.flight_zones").joinpath(self._flight_zone_name)
        self._max_relative_altitude = 10.0

        # Init flight variables
        self.latitude, self.longitude, self.relative_altitude = None, None, None
        self.pitch, self.roll, self.heading = None, None, None
        self.home_altitude = None

        # Load fligth zone
        self._flight_zone = self.load_fligth_zone()
        self.__system = None

    @classmethod
    async def connect(cls, serial_device='/dev/ttyUSB0', serial_baud=921600, use_sim=False):
        self = cls()
        self.__system = System()
        # Init position and wait for home position
        await self.wait_for_connection(serial_device, serial_baud, use_sim)
        await self.wait_for_home()
        self._update_position_task = asyncio.create_task(self._update_position())
        self._update_attitude_task = asyncio.create_task(self._update_attitude())
        return self

    async def _update_position(self):
        async for position in self.__system.telemetry.position():
            self.latitude, self.longitude, self.relative_altitude = position.latitude_deg, position.longitude_deg, position.relative_altitude_m

    async def _update_attitude(self):
        async for attitude_euler in self.__system.telemetry.attitude_euler():
            self.pitch, self.roll, self.heading = attitude_euler.pitch_deg, attitude_euler.roll_deg, attitude_euler.yaw_deg

    async def wait_for_connection(self, serial_device, serial_baud, use_sim):
        if use_sim:
            system_address = "udp://:14540"
        else:
            system_address = f"serial:///{serial_device}:{serial_baud}"
        
        await self.__system.connect(system_address=system_address)

        print("Waiting for UAV to connect...")
        async for state in self.__system.core.connection_state():
            if state.is_connected:
                print(f"Connected to UAV!\n")
                break

    async def wait_for_home(self):
        print("Waiting for UAV to have a global position estimate...")
        async for health in self.__system.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print("Global position state is good enough for flying.\n")
                break

        print("Fetching absolute altitude at home location...")
        async for terrain_info in self.__system.telemetry.home():
            self.home_altitude = terrain_info.absolute_altitude_m
            print(f"Absolute home altitude is {self.home_altitude:.1f} m.")
            break
    
    async def arm_and_takeoff(self, takeoff_altitude: float|int=2):
        """Arm and takeoff UAV to `takeoff_altitude`"""
        if takeoff_altitude > self._max_relative_altitude:
            print(f"Takeoff altitude higher than the allowed {self._max_relative_altitude:.1f} m.")
            return False
        
        try:
            await self.__system.action.set_takeoff_altitude(takeoff_altitude)
            print("Arming")
            await self.__system.action.arm()
            print("Taking off")
            await self.__system.action.takeoff()
            return True
        except Exception as e:
                print(f"Failed with: {e}")
                return False

    async def land(self):
        """Land UAV"""
        try:
            print("Landing")
            await self.__system.action.land()
            return True
        except Exception as e:
                print(f"Failed with: {e}")
                return False

    async def send_goal_position(self, latitude: float, longitude: float, relative_altitude: float|int, heading: float|int=None) -> bool:
        """Send goal position in the following format: `latitude` and `longitude` in WGS84 coordinates,
        `relative_altitude` in meters and `heading` in degrees. If no `heading` is specified the UAV uses automatic heading and is orientated in flight direction.
        If a heading is specified the UAV immediately turns to that heading and then proceeds to its goal position.
        Returns wether the goal position is accepted or not as a bool."""
        position_allowed, altitude_allowed = self.check_goal_position(latitude, longitude, relative_altitude)
        if not heading:
            heading = float("nan")  # nan translates to no new heading
        else:
            heading = float(heading)
        # Build command if goal is allowed
        if position_allowed and altitude_allowed and self.home_altitude is not None: 
            try:
                await self.__system.action.goto_location(latitude, longitude, self.home_altitude + relative_altitude, heading)
                print("Position sent to UAV.")
                return True
            except Exception as e:
                print(f"Failed with: {e}")
                return False
        elif self.home_altitude is None:
            print("No home position yet.")
            return False
        else:
            if not position_allowed:
                print("Rejected: Position not in flight zone.")
            if not altitude_allowed:
                print(f"Rejected: Altitude is higher than the allowed {self._max_relative_altitude:.1f} m.")
            return False

    def check_goal_position(self, latitude, longitude, relative_altitude):
        if not self._flight_zone:
            print("Unable to send command as flight zone is not set.")
            return False, False
        
        position_allowed, altitude_allowed = True, True
        goal_position = Point([latitude, longitude])
        # Check altitude restriction
        if relative_altitude > self._max_relative_altitude:
            altitude_allowed = False
        # Check if goal position is within flight zone
        if not self._flight_zone.contains(goal_position):
            position_allowed = False
        return position_allowed, altitude_allowed
    
    def load_fligth_zone(self):
        try:
            with open(self._flight_zone_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(e)
            return None

        json_polygons = data['geoFence']['polygons']

        # Check if polygon is inclusion or exclusion polygon
        if len(json_polygons) == 1 and json_polygons[0]['inclusion']:
            polygon_points = []
            for point in json_polygons[0]['polygon']:
                polygon_point = [point[0], point[1]]
                polygon_points.append(polygon_point)
            shapely_polygon = Polygon(polygon_points)
            print(f"Flight zone loaded from file {self._flight_zone_name}, maximum relative altitude set to {self._max_relative_altitude:.1f} m.\n")
            return shapely_polygon
        else:
            raise ValueError("Either multiple inclusion zones or only exclusion zone(s) found in flight zones file.")

def main(args=None):
    node = UAV()
    
    
if __name__ == '__main__':
    main()
