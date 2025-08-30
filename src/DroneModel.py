import threading
import asyncio
import math

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from VehicleStatus import VehicleStatus, FlightMode, Position, Attitude, Velocity

import mavsdk
from mavsdk import System
from mavsdk.action import ActionError

ALLOWABLE_HORIZONTAL_DISTANCE_TO_WAYPOINT = 1.0
ALLOWABLE_VERTICAL_DISTANCE_TO_WAYPOINT = 1.0


class DroneModel(QObject):
    ui_update_signal = pyqtSignal()

    def __init__(self, connection_address: str = "udp://:14540"):
        super().__init__()
        self.drone = System()
        self.connection_address = connection_address
        self.connected = False
        self.coordinates = []

        self._waypoints: list['Position'] = []
        self._vehicle_status = VehicleStatus()

        self._vehicle_status_lock = threading.Lock()
        self._waypoints_lock = threading.Lock()

        self.running = False
        self.main_task = None
        self.ui_updater_task = None
        self.event_loop = None
        self.loop_ready_event = threading.Event()
        self.thread = None

        self._initialize_status()

    def _initialize_status(self):
        self._vehicle_status.heartbeat = False
        self._vehicle_status.armed = False
        self._vehicle_status.in_air = False
        self._vehicle_status.position = Position(0.0, 0.0, 0.0)
        self._vehicle_status.attitude = Attitude(0.0, 0.0, 0.0)
        self._vehicle_status.velocity = Velocity(0.0, 0.0, 0.0)
        self._vehicle_status.battery_percentage = 0.0
        self._vehicle_status.battery_voltage = 0.0
        self._vehicle_status.flight_mode = FlightMode.MANUAL
    
    def _run_event_loop(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()
        
    def run_async(self, coro):
        if self.event_loop is None or not self.event_loop.is_running():
            return None
        
        future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)
        result = future.result(10)
        return result
        

    async def connect(self):
        await self.drone.connect(system_address=self.connection_address)
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                break
            
    async def set_attitude_pid_params(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "roll"):
        try:
            if axis.lower() == "roll":
                await self.drone.param.set_param_float("MC_ROLL_P", p_gain)
            elif axis.lower() == "pitch":
                await self.drone.param.set_param_float("MC_PITCH_P", p_gain)
            elif axis.lower() == "yaw":
                await self.drone.param.set_param_float("MC_YAW_P", p_gain)

            return True
        except Exception as e:
            print(e)
            return False

    def set_attitude_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "roll"):
        if self.event_loop is None or not self.event_loop.is_running():
            return False
        return self.run_async(self.set_attitude_pid_params(p_gain, i_gain, d_gain, axis))

    async def get_attitude_pid_params(self, axis: str = "roll"):
        try:
            if axis.lower() == "roll":
                p = await self.drone.param.get_param_float("MC_ROLL_P")
                # Attitude controller only has P gain, no I or D
                return {"p": p, "i": 0.0, "d": 0.0}
            elif axis.lower() == "pitch":
                p = await self.drone.param.get_param_float("MC_PITCH_P")
                return {"p": p, "i": 0.0, "d": 0.0}
            elif axis.lower() == "yaw":
                p = await self.drone.param.get_param_float("MC_YAW_P")
                return {"p": p, "i": 0.0, "d": 0.0}
            return {"p": 0.0, "i": 0.0, "d": 0.0}
        except Exception as e:
            print(e)
            return {"p": 0.0, "i": 0.0, "d": 0.0}

          
    def get_attitude_pid_params_sync(self, axis: str = "roll"):
        if self.event_loop is None or not self.event_loop.is_running():
            return {"p": 0.0, "i": 0.0, "d": 0.0}
        return self.run_async(self.get_attitude_pid_params(axis))



    async def get_rate_pid_params(self, axis: str = "roll"):
        try:
            if axis.lower() == "roll":
                p = await self.drone.param.get_param_float("MC_ROLLRATE_P")
                i = await self.drone.param.get_param_float("MC_ROLLRATE_I")
                d = await self.drone.param.get_param_float("MC_ROLLRATE_D")
                return {"p": p, "i": i, "d": d}
            elif axis.lower() == "pitch":
                p = await self.drone.param.get_param_float("MC_PITCHRATE_P")
                i = await self.drone.param.get_param_float("MC_PITCHRATE_I")
                d = await self.drone.param.get_param_float("MC_PITCHRATE_D")
                return {"p": p, "i": i, "d": d}
            elif axis.lower() == "yaw":
                p = await self.drone.param.get_param_float("MC_YAWRATE_P")
                i = await self.drone.param.get_param_float("MC_YAWRATE_I")
                d = await self.drone.param.get_param_float("MC_YAWRATE_D")
                return {"p": p, "i": i, "d": d}
            return {"p": 0.0, "i": 0.0, "d": 0.0}
        except Exception as e:
            print(e)
            return {"p": 0.0, "i": 0.0, "d": 0.0}
    
    def get_rate_pid_params_sync(self, axis: str = "roll"):
        return self.run_async(self.get_rate_pid_params(axis))
    
    async def set_position_pid_params(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "x"):
        try:
            if axis.lower() in ["x", "y"]:
                await self.drone.param.set_param_float("MPC_XY_P", p_gain)
                await self.drone.param.set_param_float("MPC_XY_VEL_P_ACC", i_gain)
                await self.drone.param.set_param_float("MPC_XY_VEL_D_ACC", d_gain)
            elif axis.lower() == "z":
                await self.drone.param.set_param_float("MPC_Z_P", p_gain)
                await self.drone.param.set_param_float("MPC_Z_VEL_P_ACC", i_gain)
                await self.drone.param.set_param_float("MPC_Z_VEL_D_ACC", d_gain)
            return True
        except Exception as e:
            print(e)
            return False
    

    
    async def get_position_pid_params(self, axis: str = "x"):
        try:
            if axis.lower() in ["x", "y"]:
                p = await self.drone.param.get_param_float("MPC_XY_P")
                # Position controller only has P gain, no I or D
                return {"p": p, "i": 0.0, "d": 0.0}
            elif axis.lower() == "z":
                p = await self.drone.param.get_param_float("MPC_Z_P")
                return {"p": p, "i": 0.0, "d": 0.0}
            return {"p": 0.0, "i": 0.0, "d": 0.0}
        except Exception as e:
            print(e)
            return {"p": 0.0, "i": 0.0, "d": 0.0}
    
    def get_position_pid_params_sync(self, axis: str = "x"):
        return self.run_async(self.get_position_pid_params(axis))

    
    def set_velocity_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "x"):
        if self.event_loop is None or not self.event_loop.is_running():
            return False
        return self.run_async(self.set_velocity_pid_params(p_gain, i_gain, d_gain, axis))
    
    async def get_velocity_pid_params(self, axis: str = "x"):
        try:
            if axis.lower() in ["x", "y"]:
                p = await self.drone.param.get_param_float("MPC_XY_VEL_P_ACC")
                i = await self.drone.param.get_param_float("MPC_XY_VEL_I_ACC")
                d = await self.drone.param.get_param_float("MPC_XY_VEL_D_ACC")
                return {"p": p, "i": i, "d": d}
            elif axis.lower() == "z":
                p = await self.drone.param.get_param_float("MPC_Z_VEL_P_ACC")
                i = await self.drone.param.get_param_float("MPC_Z_VEL_I_ACC")
                d = await self.drone.param.get_param_float("MPC_Z_VEL_D_ACC")
                return {"p": p, "i": i, "d": d}
            return {"p": 0.0, "i": 0.0, "d": 0.0}
        except Exception as e:
            return {"p": 0.0, "i": 0.0, "d": 0.0}
    
    def get_velocity_pid_params_sync(self, axis: str = "x"):
        return self.run_async(self.get_velocity_pid_params(axis))

    
    def set_all_attitude_pid_params(self, roll_pid: dict, pitch_pid: dict, yaw_pid: dict):
        try:
            if "p" in roll_pid:
                self.set_attitude_pid_params_sync(roll_pid["p"], 0, 0, "roll")
            if "p" in pitch_pid:
                self.set_attitude_pid_params_sync(pitch_pid["p"], 0, 0, "pitch")
            if "p" in yaw_pid:
                self.set_attitude_pid_params_sync(yaw_pid["p"], 0, 0, "yaw")
            return True
        except Exception as e:
            print(e)
            return False
    
    def set_all_rate_pid_params(self, roll_pid: dict, pitch_pid: dict, yaw_pid: dict):
        try:
            if all(k in roll_pid for k in ["p", "i", "d"]):
                self.set_rate_pid_params_sync(roll_pid["p"], roll_pid["i"], roll_pid["d"], "roll")
            if all(k in pitch_pid for k in ["p", "i", "d"]):
                self.set_rate_pid_params_sync(pitch_pid["p"], pitch_pid["i"], pitch_pid["d"], "pitch")
            if all(k in yaw_pid for k in ["p", "i", "d"]):
                self.set_rate_pid_params_sync(yaw_pid["p"], yaw_pid["i"], yaw_pid["d"], "yaw")
            return True
        except Exception as e:
            print(e)
            return False
    
    def set_all_position_pid_params(self, xy_pid: dict, z_pid: dict):
        try:
            if all(k in xy_pid for k in ["p", "i", "d"]):
                self.set_position_pid_params_sync(xy_pid["p"], xy_pid["i"], xy_pid["d"], "x")
            if all(k in z_pid for k in ["p", "i", "d"]):
                self.set_position_pid_params_sync(z_pid["p"], z_pid["i"], z_pid["d"], "z")
            return True
        except Exception as e:
            print(e)
            return False
    
    def set_all_velocity_pid_params(self, xy_pid: dict, z_pid: dict):
        try:
            if all(k in xy_pid for k in ["p", "i", "d"]):
                self.set_velocity_pid_params_sync(xy_pid["p"], xy_pid["i"], xy_pid["d"], "x")
            if all(k in z_pid for k in ["p", "i", "d"]):
                self.set_velocity_pid_params_sync(z_pid["p"], z_pid["i"], z_pid["d"], "z")
            return True
        except Exception as e:
            print(e)
            return False
    
    async def set_rate_pid_params(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "roll"):
        try:
            param_name_p = f"MC_{axis.upper()}RATE_P"
            param_name_i = f"MC_{axis.upper()}RATE_I"
            param_name_d = f"MC_{axis.upper()}RATE_D"

            
            await self.drone.param.set_param_float(param_name_p, p_gain)
            await self.drone.param.set_param_float(param_name_i, i_gain)
            await self.drone.param.set_param_float(param_name_d, d_gain)
            return True
        except Exception as e:
            print(e)
            return False
    
    def set_rate_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "roll"):
        return self.run_async(self.set_rate_pid_params(p_gain, i_gain, d_gain, axis))
    


    def set_position_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "x"):
        return self.run_async(self.set_position_pid_params(p_gain, i_gain, d_gain, axis))

    
    async def set_velocity_pid_params(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "x"):
        try:
            if axis.lower() == "x" or axis.lower() == "y":
                param_name_p = "MPC_XY_VEL_P_ACC"
                param_name_i = "MPC_XY_VEL_I_ACC"
                param_name_d = "MPC_XY_VEL_D_ACC"
            elif axis.lower() == "z":
                param_name_p = "MPC_Z_VEL_P_ACC"
                param_name_i = "MPC_Z_VEL_I_ACC"
                param_name_d = "MPC_Z_VEL_D_ACC"
            else:
                return False

            await self.drone.param.set_param_float(param_name_p, p_gain)
            await self.drone.param.set_param_float(param_name_i, i_gain)
            await self.drone.param.set_param_float(param_name_d, d_gain)
            return True
        except Exception as e:
            print(e)
            return False

    

    def get_all_pid_parameters(self):
        try:
            params = {
                'attitude': {
                    'roll': self.get_attitude_pid_params_sync('roll'),
                    'pitch': self.get_attitude_pid_params_sync('pitch'),
                    'yaw': self.get_attitude_pid_params_sync('yaw')
                },
                'rate': {
                    'roll': self.get_rate_pid_params_sync('roll'),
                    'pitch': self.get_rate_pid_params_sync('pitch'),
                    'yaw': self.get_rate_pid_params_sync('yaw')
                },
                'position': {
                    'x': self.get_position_pid_params_sync('x'),
                    'y': self.get_position_pid_params_sync('y'),
                    'z': self.get_position_pid_params_sync('z')
                },
                'velocity': {
                    'x': self.get_velocity_pid_params_sync('x'),
                    'y': self.get_velocity_pid_params_sync('y'),
                    'z': self.get_velocity_pid_params_sync('z')
                }
            }
            return params
        except Exception as e:
            print(e)
            return None



    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_async_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.event_loop and self.main_task:
            asyncio.run_coroutine_threadsafe(self._stop_async(), self.event_loop)
        if self.thread:
            self.thread.join(timeout=5.0)

    def _run_async_loop(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        self.loop_ready_event.set()
        self.main_task = self.event_loop.create_task(self._main_async())
        self.event_loop.run_forever()
        self.event_loop.close()

    async def _main_async(self):
        try:
            await self.drone.connect(system_address=self.connection_address)

            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    with self._vehicle_status_lock:
                        self._vehicle_status.heartbeat = True
                        break

            tasks = [
                self._monitor_health(),
                self._monitor_position(),
                self._monitor_attitude(),
                self._monitor_velocity(),
                self._monitor_battery(),
                self._monitor_flight_mode(),
                self._monitor_armed_state(),
                self._monitor_in_air_state(),
                self._monitor_connection(),
                self._update_ui_periodic()
            ]

            await asyncio.gather(*tasks)


        except Exception as e:
            print(e)

    async def _stop_async(self):
        self.running = False
        if self.main_task:
            self.main_task.cancel()

        if self.ui_updater_task:
            self.ui_updater_task.cancel()

    async def _update_ui_periodic(self, interval: float = 0.5):
        while self.running:
            self.ui_update_signal.emit()

            await asyncio.sleep(interval)

    async def _monitor_health(self):
        try:
            async for health in self.drone.telemetry.health():
                if not self.running:
                    break
        except Exception as e:
            print(e)

    async def _monitor_position(self):
        try:
            async for position in self.drone.telemetry.position():
                if not self.running:
                    break
                with self._vehicle_status_lock:
                    self._vehicle_status.position.latitude = position.latitude_deg
                    self._vehicle_status.position.longitude = position.longitude_deg
                    self._vehicle_status.position.altitude = position.relative_altitude_m

                with self._waypoints_lock:
                    if len(self._waypoints) > 0:
                        horizontal_distance = self.haversine(position.latitude_deg,
                                                             position.longitude_deg,
                                                             self._waypoints[0].latitude,
                                                             self._waypoints[0].longitude)
                        vertical_distance = np.fabs(position.relative_altitude_m - self._waypoints[0].altitude)
                        if (horizontal_distance < ALLOWABLE_HORIZONTAL_DISTANCE_TO_WAYPOINT) and (
                                vertical_distance < ALLOWABLE_VERTICAL_DISTANCE_TO_WAYPOINT):
                            print("MOVE COMPLETE")
                            self._waypoints.pop(0)
        except Exception as e:
            print(e)

    async def _monitor_attitude(self):
        try:
            async for attitude in self.drone.telemetry.attitude_euler():
                if not self.running:
                    break

                with self._vehicle_status_lock:
                    self._vehicle_status.attitude.roll = math.radians(attitude.roll_deg)
                    self._vehicle_status.attitude.pitch = math.radians(attitude.pitch_deg)
                    self._vehicle_status.attitude.yaw = math.radians(attitude.yaw_deg)
        except Exception as e:
            print(e)

    async def _monitor_velocity(self):
        try:
            async for velocity in self.drone.telemetry.velocity_ned():
                if not self.running:
                    break

                with self._vehicle_status_lock:
                    self._vehicle_status.velocity.vx = velocity.north_m_s
                    self._vehicle_status.velocity.vy = velocity.east_m_s
                    self._vehicle_status.velocity.vz = velocity.down_m_s
        except Exception as e:
            print(e)

    async def _monitor_battery(self):
        try:
            async for battery in self.drone.telemetry.battery():
                if not self.running:
                    break

                with self._vehicle_status_lock:
                    self._vehicle_status.battery_percentage = battery.remaining_percent
                    self._vehicle_status.battery_voltage = battery.voltage_v
        except Exception as e:
            print(e)

    async def _monitor_flight_mode(self):
        try:
            async for flight_mode in self.drone.telemetry.flight_mode():
                if not self.running:
                    break

                with self._vehicle_status_lock:
                    if flight_mode == mavsdk.system.telemetry.FlightMode.MANUAL:
                        self._vehicle_status.flight_mode = FlightMode.MANUAL
                    elif flight_mode == mavsdk.system.telemetry.FlightMode.MISSION:
                        self._vehicle_status.flight_mode = FlightMode.MISSION
                    elif flight_mode == mavsdk.system.telemetry.FlightMode.LAND:
                        self._vehicle_status.flight_mode = FlightMode.LANDING
                    else:
                        self._vehicle_status.flight_mode = FlightMode.MANUAL

        except Exception as e:
            print(e)

    async def _monitor_armed_state(self):
        try:
            async for armed in self.drone.telemetry.armed():
                if not self.running:
                    break

                with self._vehicle_status_lock:
                    self._vehicle_status.armed = armed
        except Exception as e:
            print(e)

    async def _monitor_in_air_state(self):
        try:
            async for in_air in self.drone.telemetry.in_air():
                if not self.running:
                    break

                with self._vehicle_status_lock:
                    self._vehicle_status.in_air = in_air
        except Exception as e:
            print(e)

    async def _monitor_connection(self):
        try:
            async for state in self.drone.core.connection_state():
                if not self.running:
                    break

                with self._vehicle_status_lock:
                    self._vehicle_status.heartbeat = state.is_connected
        except Exception as e:
            print(e)

    def status(self):
        return self._vehicle_status

    async def arm(self):
        try:
            if await self.preflight_check():
                await self.drone.action.arm()
            else:
                return False
            return True
        except ActionError as e:
            return False

    def arm_sync(self):
        return self.run_async(self.arm())

    async def disarm(self):
        try:
            await self.drone.action.disarm()
            return True
        except ActionError as e:
            return False

    def disarm_sync(self):
        return self.run_async(self.disarm())

    async def takeoff(self, altitude):
        try:
            await self.drone.action.set_takeoff_altitude(altitude)
            await self.drone.action.takeoff()
            return True
        except ActionError as e:
            print(e)
            return False

    def takeoff_sync(self, altitude):
        return self.run_async(self.takeoff(altitude))

    async def land(self):
        try:
            await self.drone.action.land()
            return True
        except ActionError as e:
            print(e)
            return False

    def land_sync(self):
        return self.run_async(self.land())

    async def preflight_check(self) -> bool:
        checks_passed = True

        async for health in self.drone.telemetry.health():
            if not health.is_armable:
                checks_passed = False
            break

        async for in_air in self.drone.telemetry.in_air():
            if in_air:
                checks_passed = False
            break

        return checks_passed

    async def goto_location(self, pos: 'Position'):
        try:
            await self.drone.action.goto_location(pos.latitude, pos.longitude, pos.altitude, 0)
            return True
        except ActionError as e:
            print(e)
            return False

    # --------------------------------
    # Helper methods

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float):
        earth_radius = 6371000
        d_lat = np.radians(lat2 - lat1)
        d_lon = np.radians(lon2 - lon1)

        origin_lat = np.radians(lat1)
        destination_lat = np.radians(lat2)

        a = np.sin(d_lat / 2) ** 2 + np.sin(d_lon / 2) ** 2 * np.cos(origin_lat) * np.cos(destination_lat)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        return earth_radius * c

    # --------------------------------

    async def _update_waypoints_on_drone(self):
        while len(self._waypoints) > 0:
            val = await self.goto_location(self._waypoints[0])
            if not val:
                print("move failed")

    # --------------------------------
    # Public stuff

    def add_waypoint_to_end(self, new_pos: 'Position'):
        self.loop_ready_event.wait()

        with self._waypoints_lock:
            self._waypoints.append(new_pos)

        if len(self._waypoints) == 1:
            asyncio.run_coroutine_threadsafe(self._update_waypoints_on_drone(), self.event_loop)

    def remove_waypoint(self, index: int):
        print(index)
        with self._waypoints_lock:
            self._waypoints.pop(index)

    def get_waypoints(self):
        with self._waypoints_lock:
            return self._waypoints

    def get_vehicle_status(self):
        with self._vehicle_status_lock:
            return self._vehicle_status

    def __del__(self):
        if hasattr(self, 'loop') and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        if hasattr(self, 'control_thread') and self.control_thread.is_alive():
            self.control_thread.join(timeout=1.0)
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
