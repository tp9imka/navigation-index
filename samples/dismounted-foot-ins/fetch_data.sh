#!/bin/sh
# Fetch the pyshoe hallway trials (processed .mat, ~2 MB each, 36 trials, ~85 MB) and the raw
# magnetometer logs of 6 walk trials (~6 MB each) into data/hallway/. Source: the UTIAS FTP
# that pyshoe's download_data.sh points at (also on IEEE DataPort:
# https://ieee-dataport.org/open-access/university-toronto-foot-mounted-inertial-navigation-dataset).
set -eu
B=ftp://128.100.201.179/2019-pyshoe/data/hallway
D=$(dirname "$0")/data/hallway
mkdir -p "$D"
for mode in walk run comb; do
  for subj in 0 1 2 3 4; do
    for trial in $(curl -s -m 30 "$B/$mode/$subj/" | awk '{print $NF}'); do
      p=$mode/$subj/$trial
      [ -s "$D/$p/processed_data.mat" ] && continue
      mkdir -p "$D/$p"
      curl -s -m 300 -o "$D/$p/processed_data.mat" "$B/$p/processed_data.mat"
      echo "$p"
    done
  done
done
for p in walk/0/2018-04-07-15-39-07 walk/0/2018-04-07-15-42-42 walk/0/2018-04-10-14-04-36 \
         walk/1/2018-04-11-10-39-53 walk/2/2018-04-11-19-42-05 walk/4/2018-04-11-15-20-30; do
  [ -s "$D/$p/imumagnetic_field.csv" ] || curl -s -m 900 -o "$D/$p/imumagnetic_field.csv" "$B/$p/imumagnetic_field.csv"
  # first 20 kB of the raw IMU log: enough to find the ROS seq of processed sample 0
  [ -s "$D/$p/imuimu_head.csv" ] || curl -s -m 60 -r 0-20000 -o "$D/$p/imuimu_head.csv" "$B/$p/imuimu.csv"
done
echo "done: $(find "$D" -name processed_data.mat | wc -l) trials"
