#!/bin/bash
# Run the SCTBench suite in a chroot of the verified PERIOD image so a
# dockerd restart does not kill the measurements.
set -u
ROOTFS=/home/qiuyang/period-root
DATA=/home/qiuyang/sctbench-data
LOG=$DATA/sctbench/suite.log
mkdir -p "$DATA/sctbench" "$ROOTFS"

export_rootfs() {
  if [ -x "$ROOTFS/workdir/PERIOD/tool/DBDS/run_PDS.py" ] && [ -d "$ROOTFS/workdir/PERIOD/.git" ]; then
    echo "rootfs already present" >> "$LOG"
    return 0
  fi
  echo "exporting image $(date -Is)" >> "$LOG"
  service docker start >> "$LOG" 2>&1 || true
  cid=$(docker create period:latest)
  docker export "$cid" | tar -C "$ROOTFS" -xf -
  docker rm "$cid" >> "$LOG"
}

mount_rootfs() {
  mkdir -p "$ROOTFS/proc" "$ROOTFS/sys" "$ROOTFS/dev" "$ROOTFS/experiment-data"
  mountpoint -q "$ROOTFS/proc" || mount --bind /proc "$ROOTFS/proc"
  mountpoint -q "$ROOTFS/sys" || mount --bind /sys "$ROOTFS/sys"
  mountpoint -q "$ROOTFS/dev" || mount --bind /dev "$ROOTFS/dev"
  mountpoint -q "$ROOTFS/experiment-data" || mount --bind "$DATA" "$ROOTFS/experiment-data"
  cp /etc/resolv.conf "$ROOTFS/etc/resolv.conf"
}

export_rootfs
mount_rootfs
echo "chroot commit $(chroot "$ROOTFS" git -C /workdir/PERIOD rev-parse HEAD)" >> "$LOG"

while [ ! -f "$DATA/sctbench/suite_finished.json" ]; do
  echo "suite start $(date -Is)" >> "$LOG"
  mount_rootfs
  chroot "$ROOTFS" python3 /experiment-data/sctbench/scripts/run_sctbench.py \
    /experiment-data/sctbench/manifest.json --suite >> "$LOG" 2>&1
  code=$?
  echo "suite exit $code $(date -Is)" >> "$LOG"
  if [ -f "$DATA/sctbench/suite_finished.json" ]; then
    break
  fi
  sleep 5
done
echo "supervisor done $(date -Is)" >> "$LOG"
