import asyncio
from dataclasses import dataclasses

@dataclasses
class VehicleStatus:
    Heartbeat: bool = False
    #Vehicle Statenya
    armed: bool = False
    in_air: bool = False
    #Position (X, Y, Z) trhadap
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    #Attitude 
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    #Batre
    battery_voltage: float = 0.0
    battery_percentage: float = 0.0
    flight_mode: str = "Manual"
    