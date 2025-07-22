import asyncio
from dataclasses import dataclasses

@dataclasses
class VehicleStatus:
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
    #Sesuai nama
    flight_mode: str = "Manual"
    #tar nambah