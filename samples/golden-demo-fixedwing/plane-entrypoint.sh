#!/bin/sh
# SERIAL0=TCP 5760, SERIAL1=TCP 5762, SERIAL2=TCP 5763. Extra args (e.g. --defaults a,b) are appended.
set -e
mkdir -p /sitl && cd /sitl
exec /ardupilot/build/sitl/bin/arduplane -S --model "${SITL_MODEL:-plane}" --speedup "${SITL_SPEEDUP:-1}" \
    --home "${SITL_HOME:--35.363261,149.165230,584,353}" \
    --defaults /ardupilot/Tools/autotest/models/plane.parm \
    --serial0 tcp:0 -I0 "$@"
