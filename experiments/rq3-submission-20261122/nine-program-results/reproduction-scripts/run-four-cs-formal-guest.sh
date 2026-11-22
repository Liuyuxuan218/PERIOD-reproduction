#!/usr/bin/env bash
set -euo pipefail
exec 3>&1 4>&2
rq3_runtime=${1:?Existing runtime required}
rq3_build=${2:?Validated build directory required}
rq3_selection=${3:-all}
rq3_repair_source=${4:-}
if test "$rq3_selection" != all; then
  [[ "$rq3_selection" =~ ^[1-3]:(3|4|5|10)(,[1-3]:(3|4|5|10))*$ ]] || exit 1
fi
case "$rq3_runtime" in /home/vagrant/rq3-period-runtime-*) ;; *) exit 1 ;; esac
case "$rq3_build" in /workdir/rq3-four-cs-*) ;; *) exit 1 ;; esac
test "$(uname -r)" = 3.16.0-77-generic
rq3_fs="$rq3_runtime/rootfs"
test -f "$rq3_fs$rq3_build/status.json"
exec 9>"$rq3_runtime/formal-measurement.lock"
flock -n 9 || { echo 'FORMAL_STOPPED: another formal batch is running'; exit 1; }
rq3_run=$(mktemp -d "$rq3_runtime/formal-XXXXXX")
rq3_inside="/workdir/rq3-$(basename "$rq3_run")"
mkdir "$rq3_fs$rq3_inside"
cat /sys/devices/system/clocksource/clocksource0/current_clocksource > "$rq3_fs$rq3_inside/runtime-clocksource.txt"
test "$(cat "$rq3_fs$rq3_inside/runtime-clocksource.txt")" = kvm-clock
cp /home/vagrant/rq3-observe-executions.py "$rq3_fs$rq3_inside/observe-executions.py"
cp /home/vagrant/rq3-run-four-cs-formal.py "$rq3_fs$rq3_inside/run-four-cs-formal.py"
rq3_dump() {
  rq3_rc=$?
  trap - EXIT
  exec 1>&3 2>&4
  echo "FORMAL_DIRECTORY=$rq3_inside"
  echo "FORMAL_GUEST_EXIT=$rq3_rc"
  if test -f "$rq3_fs$rq3_inside/summary.json"; then
    echo 'BEGIN_FORMAL_SUMMARY_JSON'
    cat "$rq3_fs$rq3_inside/summary.json"
    echo 'END_FORMAL_SUMMARY_JSON'
  fi
  cp "$rq3_run/progress.log" "$rq3_fs$rq3_inside/guest-progress.log"
  tar -C "$rq3_fs$rq3_inside" -czf "$rq3_run/evidence.tar.gz" .
  rq3_hash=$(sha256sum "$rq3_run/evidence.tar.gz" | cut -d ' ' -f 1)
  echo "FORMAL_ARCHIVE_SHA256=$rq3_hash"
  echo 'BEGIN_FORMAL_ARCHIVE_BASE64'
  base64 "$rq3_run/evidence.tar.gz"
  echo 'END_FORMAL_ARCHIVE_BASE64'
  exit "$rq3_rc"
}
trap rq3_dump EXIT
echo 'FORMAL_RUNNING: reuse validated binaries; no rebuild, installation or large archive import.'
unshare --mount -- bash -s -- "$rq3_fs" "$rq3_inside" "$rq3_build" "$rq3_selection" "$rq3_repair_source" <<'NS' 2>&1 | tee "$rq3_run/progress.log"
set -eu
rq3_fs=$1
rq3_inside=$2
rq3_build=$3
rq3_selection=$4
rq3_repair_source=$5
mount --make-rprivate /
mount -t proc proc "$rq3_fs/proc"
mount --bind /dev "$rq3_fs/dev"
chroot "$rq3_fs" /usr/bin/env -i HOME=/root LANG=C PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin LD_LIBRARY_PATH=/opt/rq3-maple-legacy/lib:/workdir/PERIOD/clang+llvm/lib PYTHONPATH=/opt/rq3-maple-legacy/python PYTHONUNBUFFERED=1 RQ3_SELECTION="$rq3_selection" RQ3_REPAIR_SOURCE="$rq3_repair_source" timeout -k 15s 7200s python3 "$rq3_inside/run-four-cs-formal.py" "$rq3_build"
NS
