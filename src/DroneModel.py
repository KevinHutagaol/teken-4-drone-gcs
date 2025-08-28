import threading
import asyncio
import math
from typing import TypedDict
from VehicleStatus import VehicleStatus, FlightMode, Position, Attitude, Velocity    
from mavsdk import System
from mavsdk.action import ActionError


class WaypointListItem(TypedDict):
    num: int
    waypoint: Position


class DroneModel:
    def __init__(self, connection_address: str = "udp://:14540"):
        self.drone = System()
        self.connection_address = connection_address
        self.connected = False
        self.coordinates = []
        self._current_pos = Position(0, 0, 0)
        self._waypoints = []
        
        self.running = False
        self.main_task = None
        self.event_loop = None
        self.thread = None
        
        self.vehicle_status = VehicleStatus()
        self._initialize_status()
    
    def _initialize_status(self):
        self.vehicle_status.heartbeat = False
        self.vehicle_status.armed = False
        self.vehicle_status.in_air = False
        self.vehicle_status.position = Position(6.366, 106.825, 0.0)
        self.vehicle_status.attitude = Attitude(0.0, 0.0, 0.0)
        self.vehicle_status.velocity = Velocity(0.0, 0.0, 0.0)
        self.vehicle_status.battery_percentage = 0.0
        self.vehicle_status.battery_voltage = 0.0
        self.vehicle_status.flight_mode = FlightMode.MANUAL
    
    def _run_event_loop(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()
        
    def run_async(self, coro):
        if self.event_loop is None or not self.event_loop.is_running():
            return asyncio.run(coro)
            
        future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)
        return future.result(10)
        
    async def connect(self):
        await self.drone.connect(system_address=self.connection_address)
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                self.connected = True
                break
    async def set_attitude_pid_params(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "roll"):
        try:
            param_name_p = f"MC_{axis.upper()}_P"
            param_name_i = f"MC_{axis.upper()}_I" 
            param_name_d = f"MC_{axis.upper()}_D"
            
            await self.drone.param.set_param_float(param_name_p, p_gain)
            await self.drone.param.set_param_float(param_name_i, i_gain)
            await self.drone.param.set_param_float(param_name_d, d_gain)
            return True
        except Exception as e:
            return False
    
    def set_attitude_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "roll"):
        return self.run_async(self.set_attitude_pid_params(p_gain, i_gain, d_gain, axis))
    
    async def get_attitude_pid_params(self, axis: str = "roll"):
        try:
            param_name_p = f"MC_{axis.upper()}_P"
            param_name_i = f"MC_{axis.upper()}_I"
            param_name_d = f"MC_{axis.upper()}_D"
            
            p_result = await self.drone.param.get_param_float(param_name_p)
            i_result = await self.drone.param.get_param_float(param_name_i)
            d_result = await self.drone.param.get_param_float(param_name_d)
            
            return {
                'p': p_result.value,
                'i': i_result.value, 
                'd': d_result.value
            }
        except Exception as e:
            return {'p': 0.0, 'i': 0.0, 'd': 0.0}
    
    def get_attitude_pid_params_sync(self, axis: str = "roll"):
        return self.run_async(self.get_attitude_pid_params(axis))
    
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
            return False
    
    def set_rate_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "roll"):
        return self.run_async(self.set_rate_pid_params(p_gain, i_gain, d_gain, axis))
    
    async def get_rate_pid_params(self, axis: str = "roll"):
        try:
            param_name_p = f"MC_{axis.upper()}RATE_P"
            param_name_i = f"MC_{axis.upper()}RATE_I"
            param_name_d = f"MC_{axis.upper()}RATE_D"
            
            p_result = await self.drone.param.get_param_float(param_name_p)
            i_result = await self.drone.param.get_param_float(param_name_i)
            d_result = await self.drone.param.get_param_float(param_name_d)
            
            return {
                'p': p_result.value,
                'i': i_result.value,
                'd': d_result.value
            }
        except Exception as e:
            return {'p': 0.0, 'i': 0.0, 'd': 0.0}
    
    def get_rate_pid_params_sync(self, axis: str = "roll"):
        return self.run_async(self.get_rate_pid_params(axis))
    
    async def set_position_pid_params(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "x"):
        try:
            if axis.lower() == "x":
                param_name_p = "MPC_XY_P"
                param_name_d = "MPC_XY_VEL_P_ACC"
            elif axis.lower() == "y":
                param_name_p = "MPC_XY_P"
                param_name_d = "MPC_XY_VEL_P_ACC"
            elif axis.lower() == "z":
                param_name_p = "MPC_Z_P"
                param_name_d = "MPC_Z_VEL_P_ACC"
            else:
                return False
            
            await self.drone.param.set_param_float(param_name_p, p_gain)
            if d_gain is not None:
                await self.drone.param.set_param_float(param_name_d, d_gain)
            return True
        except Exception as e:
            return False
    
    def set_position_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "x"):
        return self.run_async(self.set_position_pid_params(p_gain, i_gain, d_gain, axis))
    
    async def get_position_pid_params(self, axis: str = "x"):
        try:
            if axis.lower() == "x" or axis.lower() == "y":
                param_name_p = "MPC_XY_P"
                param_name_d = "MPC_XY_VEL_P_ACC"
            elif axis.lower() == "z":
                param_name_p = "MPC_Z_P"
                param_name_d = "MPC_Z_VEL_P_ACC"
            else:
                return {'p': 0.0, 'i': 0.0, 'd': 0.0}
            
            p_result = await self.drone.param.get_param_float(param_name_p)
            d_result = await self.drone.param.get_param_float(param_name_d)
            
            return {
                'p': p_result.value,
                'i': 0.0,
                'd': d_result.value
            }
        except Exception as e:
            return {'p': 0.0, 'i': 0.0, 'd': 0.0}
    
    def get_position_pid_params_sync(self, axis: str = "x"):
        return self.run_async(self.get_position_pid_params(axis))
    
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
            return False
    
    def set_velocity_pid_params_sync(self, p_gain: float, i_gain: float, d_gain: float, axis: str = "x"):
        return self.run_async(self.set_velocity_pid_params(p_gain, i_gain, d_gain, axis))
    
    async def get_velocity_pid_params(self, axis: str = "x"):
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
                return {'p': 0.0, 'i': 0.0, 'd': 0.0}
            
            p_result = await self.drone.param.get_param_float(param_name_p)
            i_result = await self.drone.param.get_param_float(param_name_i)
            d_result = await self.drone.param.get_param_float(param_name_d)
            
            return {
                'p': p_result.value,
                'i': i_result.value,
                'd': d_result.value
            }
        except Exception as e:
            return {'p': 0.0, 'i': 0.0, 'd': 0.0}
    
    def get_velocity_pid_params_sync(self, axis: str = "x"):
        return self.run_async(self.get_velocity_pid_params(axis))
    
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
            return None
    
    def set_all_attitude_pid_params(self, roll_pid: dict, pitch_pid: dict, yaw_pid: dict):
        try:
            results = []
            results.append(self.set_attitude_pid_params_sync(
                roll_pid['p'], roll_pid['i'], roll_pid['d'], 'roll'
            ))
            results.append(self.set_attitude_pid_params_sync(
                pitch_pid['p'], pitch_pid['i'], pitch_pid['d'], 'pitch'
            ))
            results.append(self.set_attitude_pid_params_sync(
                yaw_pid['p'], yaw_pid['i'], yaw_pid['d'], 'yaw'
            ))
            return all(results)
        except Exception as e:
            return False
    
    def set_all_rate_pid_params(self, roll_pid: dict, pitch_pid: dict, yaw_pid: dict):
        try:
            results = []
            results.append(self.set_rate_pid_params_sync(
                roll_pid['p'], roll_pid['i'], roll_pid['d'], 'roll'
            ))
            results.append(self.set_rate_pid_params_sync(
                pitch_pid['p'], pitch_pid['i'], pitch_pid['d'], 'pitch'
            ))
            results.append(self.set_rate_pid_params_sync(
                yaw_pid['p'], yaw_pid['i'], yaw_pid['d'], 'yaw'
            ))
            return all(results)
        except Exception as e:
            return False
    
    def set_all_position_pid_params(self, xy_pid: dict, z_pid: dict):
        try:
            results = []
            results.append(self.set_position_pid_params_sync(
                xy_pid['p'], xy_pid['i'], xy_pid['d'], 'x'
            ))
            results.append(self.set_position_pid_params_sync(
                z_pid['p'], z_pid['i'], z_pid['d'], 'z'
            ))
            return all(results)
        except Exception as e:
            return False
    
    def set_all_velocity_pid_params(self, xy_pid: dict, z_pid: dict):
        try:
            results = []
            results.append(self.set_velocity_pid_params_sync(
                xy_pid['p'], xy_pid['i'], xy_pid['d'], 'x'
            ))
            results.append(self.set_velocity_pid_params_sync(
                xy_pid['p'], xy_pid['i'], xy_pid['d'], 'y'
            ))
            results.append(self.set_velocity_pid_params_sync(
                z_pid['p'], z_pid['i'], z_pid['d'], 'z'
            ))
            return all(results)
        except Exception as e:
            return False
    
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
        self.main_task = self.event_loop.create_task(self._main_async())
        self.event_loop.run_until_complete(self.main_task)

    async def _main_async(self):
        try:
            await self.drone.connect(system_address=self.connection_address)
            
            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    self.vehicle_status.heartbeat = True
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
                self._monitor_connection()
            ]
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            pass

    async def _stop_async(self):
        self.running = False
        if self.main_task:
            self.main_task.cancel()

    async def _monitor_health(self):
        try:
            async for health in self.drone.telemetry.health():
                if not self.running:
                    break
        except Exception as e:
            pass

    async def _monitor_position(self):
        try:
            async for position in self.drone.telemetry.position():
                if not self.running:
                    break
                self.vehicle_status.position.latitude = position.latitude_deg
                self.vehicle_status.position.longitude = position.longitude_deg
                self.vehicle_status.position.altitude = position.relative_altitude_m
        except Exception as e:
            pass

    async def _monitor_attitude(self):
        try:
            async for attitude in self.drone.telemetry.attitude_euler():
                if not self.running:
                    break
                self.vehicle_status.attitude.roll = math.radians(attitude.roll_deg)
                self.vehicle_status.attitude.pitch = math.radians(attitude.pitch_deg) 
                self.vehicle_status.attitude.yaw = math.radians(attitude.yaw_deg)
        except Exception as e:
            pass

    async def _monitor_velocity(self):
        try:
            async for velocity in self.drone.telemetry.velocity_ned():
                if not self.running:
                    break
                self.vehicle_status.velocity.vx = velocity.north_m_s
                self.vehicle_status.velocity.vy = velocity.east_m_s
                self.vehicle_status.velocity.vz = velocity.down_m_s
        except Exception as e:
            pass

    async def _monitor_battery(self):
        try:
            async for battery in self.drone.telemetry.battery():
                if not self.running:
                    break
                self.vehicle_status.battery_percentage = battery.remaining_percent
                self.vehicle_status.battery_voltage = battery.voltage_v
        except Exception as e:
            pass

    async def _monitor_flight_mode(self):
        try:
            async for flight_mode in self.drone.telemetry.flight_mode():
                if not self.running:
                    break
                if flight_mode == self.drone.telemetry.FlightMode.MANUAL:
                    self.vehicle_status.flight_mode = FlightMode.MANUAL
                elif flight_mode == self.drone.telemetry.FlightMode.MISSION:
                    self.vehicle_status.flight_mode = FlightMode.MISSION
                elif flight_mode == self.drone.telemetry.FlightMode.LAND:
                    self.vehicle_status.flight_mode = FlightMode.LANDING
                else:
                    self.vehicle_status.flight_mode = FlightMode.MANUAL
        except Exception as e:
            pass

    async def _monitor_armed_state(self):
        try:
            async for armed in self.drone.telemetry.armed():
                if not self.running:
                    break
                self.vehicle_status.armed = armed
        except Exception as e:
            pass

    async def _monitor_in_air_state(self):
        try:
            async for in_air in self.drone.telemetry.in_air():
                if not self.running:
                    break
                self.vehicle_status.in_air = in_air
        except Exception as e:
            pass

    async def _monitor_connection(self):
        try:
            async for state in self.drone.core.connection_state():
                if not self.running:
                    break
                self.vehicle_status.heartbeat = state.is_connected
        except Exception as e:
            pass

    def status(self):
        return self.vehicle_status

    def add_waypoint_to_end(self, new_pos: Position):
        self._waypoints.append({'num': len(self._waypoints), 'waypoint': new_pos})

    def get_waypoints(self):
        return self._waypoints

    def set_current_pos(self, pos: Position):
        self._current_pos = pos

    def get_current_pos(self):
        return self._current_pos

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
            return False
            
    def takeoff_sync(self, altitude):
        return self.run_async(self.takeoff(altitude))
    
    async def land(self):
        try:
            await self.drone.action.land()
            return True
        except ActionError as e:
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

    async def goto_location(self, latitude: float, longitude: float, altitude: float, yaw: float = 0.0):
        try:
            await self.drone.action.goto_location(latitude, longitude, altitude, yaw)
            return True
        except ActionError as e:
            return False

    def goto_location_sync(self, latitude: float, longitude: float, altitude: float, yaw: float = 0.0):
        return self.run_async(self.goto_location(latitude, longitude, altitude, yaw))
        
    def __del__(self):
        if hasattr(self, 'loop') and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        if hasattr(self, 'control_thread') and self.control_thread.is_alive():
            self.control_thread.join(timeout=1.0)
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)