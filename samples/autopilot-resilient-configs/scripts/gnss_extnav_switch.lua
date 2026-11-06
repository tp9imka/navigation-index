-- GNSS vs ExternalNav consistency check for EKF3 (ArduPilot 4.6 Lua).
-- Dead-reckons from the GPS fix at arming with ExternalNav (VIO) velocity, never re-anchors on
-- GPS, and switches EKF3 to source set 2 (ExternalNav) once when either
--   a) GPS position is more than POS_TRIP_M from the dead-reckoned position, or
--   b) GPS velocity differs from ExternalNav velocity by more than VEL_TRIP_MPS for VEL_TRIP_S.
-- ExternalNav velocity is recovered from EKF3's own innovations, which are computed for
-- reporting even when that source is not fused (AP_NavEKF3_PosVelFusion.cpp, extNavVelInnov):
--   innov = ekf_vel - obs  =>  obs = ekf_vel - innov,  gps_vel - ext_vel = innov_ext - innov_gps
-- Needs SCR_ENABLE 1, EK3_SRC2_POSXY 6 / VELXY 6 and a VISION_SPEED_ESTIMATE stream.

local UPDATE_MS = 100
local SRC_GPS = 3
local SRC_EXTNAV = 6
local SET_EXTNAV = 1            -- set_posvelyaw_source_set index: 0 = SRC1, 1 = SRC2
local POS_TRIP_M = 25.0         -- > VIO drift over a flight (~0.06 m/s * 200 s) + GNSS noise
local VEL_TRIP_MPS = 0.7
local VEL_TRIP_S = 2.0
local VEL_LPF_S = 1.0
local INNOV_STALE_MS = 1000
local MAV_SEVERITY_WARNING = 4
local MAV_SEVERITY_INFO = 6

local dr_n, dr_e = nil, nil
local dv_n, dv_e = 0.0, 0.0
local vel_bad_ms = 0
local last_ms = nil
local last_ext_ms = 0
local switched = false
local next_report_ms = 0

local function reset()
  dr_n, dr_e, dv_n, dv_e, vel_bad_ms, last_ms = nil, nil, 0.0, 0.0, 0, nil
end

local function update()
  if switched then
    return
  end
  local now = millis():tofloat()
  if not arming:is_armed() then
    reset()
    return update, UPDATE_MS
  end
  local origin = ahrs:get_origin()
  if not origin or gps:status(0) < gps.GPS_OK_FIX_3D then
    return update, UPDATE_MS
  end
  local gne = origin:get_distance_NE(gps:location(0))
  if dr_n == nil then
    dr_n, dr_e, last_ms = gne:x(), gne:y(), now
    gcs:send_text(MAV_SEVERITY_INFO, "RESIL: DR anchored on GPS")
    return update, UPDATE_MS
  end
  local dt = (now - last_ms) * 0.001
  last_ms = now
  local ekf_vel = ahrs:get_velocity_NED()
  local innov_ext = ahrs:get_vel_innovations_and_variances_for_source(SRC_EXTNAV)
  local innov_gps = ahrs:get_vel_innovations_and_variances_for_source(SRC_GPS)
  if ekf_vel and innov_ext then
    last_ext_ms = now
    dr_n = dr_n + (ekf_vel:x() - innov_ext:x()) * dt
    dr_e = dr_e + (ekf_vel:y() - innov_ext:y()) * dt
  elseif now - last_ext_ms > INNOV_STALE_MS then
    -- no ExternalNav velocity: the check cannot run, and switching would land on a dead source
    return update, UPDATE_MS
  end
  local pos_err = math.sqrt((gne:x() - dr_n) ^ 2 + (gne:y() - dr_e) ^ 2)
  if innov_ext and innov_gps then
    local k = math.min(1.0, dt / VEL_LPF_S)
    dv_n = dv_n + k * ((innov_ext:x() - innov_gps:x()) - dv_n)
    dv_e = dv_e + k * ((innov_ext:y() - innov_gps:y()) - dv_e)
  end
  local vel_err = math.sqrt(dv_n * dv_n + dv_e * dv_e)
  if vel_err > VEL_TRIP_MPS then
    vel_bad_ms = vel_bad_ms + dt * 1000
  else
    vel_bad_ms = 0
  end
  if now >= next_report_ms then
    next_report_ms = now + 5000
    gcs:send_text(MAV_SEVERITY_INFO, string.format("RESIL: pos %.1f m vel %.2f m/s", pos_err, vel_err))
  end
  if pos_err > POS_TRIP_M or vel_bad_ms >= VEL_TRIP_S * 1000 then
    ahrs:set_posvelyaw_source_set(SET_EXTNAV)
    switched = true
    gcs:send_text(MAV_SEVERITY_WARNING, string.format("RESIL: GPS rejected pos %.1f m vel %.2f m/s, EKF src set 2",
                                                      pos_err, vel_err))
    return
  end
  return update, UPDATE_MS
end

gcs:send_text(MAV_SEVERITY_INFO, "RESIL: gnss_extnav_switch loaded")
return update()
