from VehicleStatus import Position

from typing import TypedDict

class WaypointListItem(TypedDict):
    num: int
    waypoint: Position

class VehicleControl:
    _current_pos: 'Position' = Position(-6.200000,106.816666,20)

    _waypoints: list['WaypointListItem'] = []

    def add_waypoint_to_end(self, new_pos: 'Position'):
        self._waypoints.append({'num': len(self._waypoints), 'waypoint': new_pos})

    def get_waypoints(self):
        return self._waypoints

    def set_current_pos(self, pos: 'Position'):
        self._current_pos = pos

    def get_current_pos(self):
        return self._current_pos


