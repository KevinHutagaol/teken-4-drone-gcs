from pymavlink import mavutil
from VehicleStatus import VehicleStatus,FlightMode, Position, Attitude, Velocity
import threading
import time

class VehicleCommunication:
    def __init__(self, port):
        super().__init__()
        self.connection = mavutil.mavlink_connection(port)
        
        self.running = False
        self.thread = None
        self.heartbeat_thread = None
        self.heartbeat_monitor_thread = None
        self.last_heartbeat_time = 0
        self.heartbeat_timeout = 5.0
        
        self.vehicle_status = VehicleStatus()
        self.vehicle_status.heartbeat = False
        self.vehicle_status.armed = False
        self.vehicle_status.in_air = False
        self.vehicle_status.position = Position(0.0, 0.0, 0.0)
        self.vehicle_status.attitude = Attitude(0.0, 0.0, 0.0)
        self.vehicle_status.velocity = Velocity(0.0, 0.0, 0.0)
        self.vehicle_status.battery_percentage = 0.0
        self.vehicle_status.battery_voltage = 0.0
        self.vehicle_status.flight_mode = FlightMode

    def request_data_stream(self):
        data_streams = mavutil.mavlink.MAV_DATA_STREAM_ALL | mavutil.mavlink.MAV_DATA_STREAM_EXTENDED_STATUS
        self.connection.mav.request_data_stream_send(
            self.connection.target_system,
            self.connection.target_component,
            data_streams, 
            1,  # default 1 hz
            1 
        )

    def start(self):
        self.running = True
        self.last_heartbeat_time = time.time()
        
        # Message listener thread
        self.thread = threading.Thread(target=self._listen_for_messages)
        self.thread.daemon = True  
        self.thread.start()

        # Heartbeat sender thread
        self.heartbeat_thread = threading.Thread(target=self._send_heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        
        # Heartbeat monitor thread
        self.heartbeat_monitor_thread = threading.Thread(target=self._monitor_heartbeat)
        self.heartbeat_monitor_thread.daemon = True
        self.heartbeat_monitor_thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2.0)
        if self.heartbeat_monitor_thread:
            self.heartbeat_monitor_thread.join(timeout=2.0)

    def _listen_for_messages(self):
        self.connection.wait_heartbeat()

        self.request_data_stream() 

        # Message check
        while self.running:
            msg = self.connection.recv_match(blocking=True, timeout=1.0)
            if msg is not None:
                self._handle_message(msg)

    def _handle_message(self, msg):
        msg_type = msg.get_type()

        if msg_type == 'HEARTBEAT':
            self._handle_heartbeat(msg)
        elif msg_type == 'GLOBAL_POSITION_INT':
            self._handle_global_position(msg)
        elif msg_type == 'ATTITUDE':
            self._handle_attitude(msg)
        elif msg_type == 'LOCAL_POSITION_NED':
            self._handle_local_position_ned(msg)
        elif msg_type == 'SYS_STATUS':
            self._handle_battery_status(msg)
        elif msg_type == 'EXTENDED_SYS_STATE':
            self._handle_ext_sys_state(msg)

    def _send_heartbeat(self):
        while self.running:
            self.connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            time.sleep(1)

    def _handle_local_position_ned(self, msg):
        self.vehicle_status.velocity.vx = msg.vx  # North 
        self.vehicle_status.velocity.vy = msg.vy  # East  
        self.vehicle_status.velocity.vz = msg.vz  # Down 

    def _handle_battery_status(self, msg):
        if hasattr(msg, 'voltage_battery'):
            self.vehicle_status.battery_voltage = msg.voltage_battery / 1000.0
        if hasattr(msg, 'battery_remaining'):
            self.vehicle_status.battery_percentage = msg.battery_remaining

    def _handle_heartbeat(self, msg):
        self.vehicle_status.heartbeat = True
        self.last_heartbeat_time = time.time()
        self.vehicle_status.armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
        
        # Flight mode
        if hasattr(msg, 'custom_mode'):
            # TODO: check for more flight modes on mavlink message 
            self.vehicle_status.flight_mode = FlightMode.MANUAL if msg.custom_mode == 0 else FlightMode.MISSION

    def _handle_global_position(self, msg):
        self.vehicle_status.position.latitude = msg.lat / 1e7  
        self.vehicle_status.position.longitude = msg.lon / 1e7
        self.vehicle_status.position.altitude = msg.alt / 1000.0 

    def _handle_attitude(self, msg):
        self.vehicle_status.attitude.roll = msg.roll
        self.vehicle_status.attitude.pitch = msg.pitch
        self.vehicle_status.attitude.yaw = msg.yaw

    def _handle_ext_sys_state(self, msg):
        if hasattr(msg, 'landed_state'):
            if msg.landed_state == mavutil.mavlink.MAV_LANDED_STATE_IN_AIR:
                self.vehicle_status.in_air = True
            elif msg.landed_state == mavutil.mavlink.MAV_LANDED_STATE_ON_GROUND:
                self.vehicle_status.in_air = False
            elif msg.landed_state == mavutil.mavlink.MAV_LANDED_STATE_TAKEOFF:
                self.vehicle_status.in_air = True  
            elif msg.landed_state == mavutil.mavlink.MAV_LANDED_STATE_LANDING:
                self.vehicle_status.in_air = True 
            else:
                pass

    def _monitor_heartbeat(self):
        while self.running:
            current_time = time.time()
            if current_time - self.last_heartbeat_time > self.heartbeat_timeout:
                if self.vehicle_status.heartbeat: 
                    self.vehicle_status.heartbeat = False
            time.sleep(0.5)

    def status(self):
        return self.vehicle_status