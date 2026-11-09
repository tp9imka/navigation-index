"""Platform drivers for the Adapter protocol. Status: unrun, written from docs.

Importing this package needs no SDK: each driver imports its SDK inside `connect()`.
See README.md in this folder for the platform table and the bench checks.
"""
from .ardupilot_pymavlink import ArduPilotPymavlinkAdapter  # noqa: F401
from .crazyflie_cflib import CrazyflieCflibAdapter  # noqa: F401
from .px4_mavsdk import Px4MavsdkAdapter  # noqa: F401
from .tello_djitellopy import TelloDjitellopyAdapter  # noqa: F401
