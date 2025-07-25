import asyncio
from dataclasses import dataclass
from enum import Enum


class FlightMode(Enum):
    MANUAL = 0
    MISSION = 1


@dataclass
class Position:
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0

    def __init__(self, lat, lon, alt):
        self.latitude = lat
        self.longitude = lon
        self.altitude = alt

    # TODO: More stuff that is useful for position vectors


@dataclass
class Attitude:
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    def __init__(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    # TODO: More stuff that is useful for attitude


class VehicleStatus:
    heartbeat: bool
    # Vehicle State
    armed: bool
    in_air: bool
    # Position (X, Y, Z)
    position: Position
    # Attitude
    attitude: Attitude
    # Battery
    battery_voltage: float
    battery_percentage: float
    flight_mode: FlightMode

