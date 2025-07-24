import asyncio
from dataclasses import dataclass
from enum import Enum


class FlightMode(Enum):
    MANUAL = 0
    MISSION = 1


@dataclass
class VehicleStatus:
    Heartbeat: bool = False
    # Vehicle State
    armed: bool = False
    in_air: bool = False
    # Position (X, Y, Z)
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    # Attitude
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    # Battery
    battery_voltage: float = 0.0
    battery_percentage: float = 0.0
    flight_mode: FlightMode = FlightMode.MANUAL
