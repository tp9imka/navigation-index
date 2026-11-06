#!/bin/sh
# MAV_BROADCAST/-t not needed: clients share this container's network namespace (see README).
set -e
mkdir -p /px4/rootfs && cd /px4/rootfs
export PX4_SIM_MODEL="${PX4_SIM_MODEL:-sihsim_quadx}"
exec /px4/bin/px4 -d /px4/etc "$@"
