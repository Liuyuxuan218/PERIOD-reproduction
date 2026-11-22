#!/usr/bin/env bash
set -euo pipefail
exec 3>&1 4>&2
rq3_runtime=${1:?Existing runtime required}
rq3_upload=${2:?Unique upload directory required}
rq3_selection=${3:?Explicit selection required}
[[ "$rq3_selection" == all || "$rq3_selection" == repair-iwsqws-rep3 ]] || exit 1
[[ "$rq3_runtime" =~ ^/home/vagrant/rq3-period-runtime-[A-Za-z0-9]+$ ]] || exit 1
[[ "$rq3_upload" =~ ^/home/vagrant/rq3-extra-formal-upload-[A-Za-z0-9-]+$ ]] || exit 1
rq3_fs="$rq3_runtime/rootfs"
test "$(uname -r)" = 3.16.0-77-generic
test "$(cat /sys/devices/system/clocksource/clocksource0/current_clocksource)" = kvm-clock
test -f "$rq3_fs/workdir/rq3-cross-family-screen-o5n8qz/summary.json"
exec 9>"$rq3_runtime/formal-measurement.lock"
flock -n 9 || { echo 'FORMAL_STOPPED: another batch is running'; exit 1; }
rq3_run=$(mktemp -d "$rq3_runtime/five-extra-formal-XXXXXX")
rq3_inside="/workdir/rq3-$(basename "$rq3_run")"
mkdir "$rq3_fs$rq3_inside"
cat /sys/devices/system/clocksource/clocksource0/current_clocksource > "$rq3_fs$rq3_inside/runtime-clocksource.txt"
for rq3_name in observe-cross-family.py cross-family-formal-support.py run-five-extra-formal.py five-extra-approved-plan.json; do
  cp "$rq3_upload/$rq3_name" "$rq3_fs$rq3_inside/"
done
cp "$rq3_upload/five-extra-budget-amendment.md" "$rq3_fs$rq3_inside/"
if [[ "$rq3_selection" == repair-iwsqws-rep3 ]]; then
  cp "$rq3_upload/repair-provenance.json" "$rq3_fs$rq3_inside/"
fi
rq3_dump() {
  rq3_rc=$?
  trap - EXIT
  exec 1>&3 2>&4
  echo "FORMAL_DIRECTORY=$rq3_inside"
  echo "FORMAL_GUEST_EXIT=$rq3_rc"
  if test -f "$rq3_fs$rq3_inside/summary.json"; then
    echo BEGIN_FORMAL_SUMMARY_JSON
    cat "$rq3_fs$rq3_inside/summary.json"
    echo END_FORMAL_SUMMARY_JSON
  fi
  cp "$rq3_run/progress.log" "$rq3_fs$rq3_inside/guest-progress.log"
  tar -C "$rq3_fs$rq3_inside" -czf "$rq3_run/evidence.tar.gz" .
  echo "FORMAL_ARCHIVE_SHA256=$(sha256sum "$rq3_run/evidence.tar.gz" | cut -d ' ' -f 1)"
  echo BEGIN_FORMAL_ARCHIVE_BASE64
  base64 "$rq3_run/evidence.tar.gz"
  echo END_FORMAL_ARCHIVE_BASE64
  exit "$rq3_rc"
}
trap rq3_dump EXIT
echo "FORMAL_RUNNING: selection=$rq3_selection; reuse binaries; no rebuild."
unshare --mount --ipc -- bash -s -- "$rq3_fs" "$rq3_inside" "$rq3_selection" <<'NS' 2>&1 | tee "$rq3_run/progress.log"
set -eu
rq3_fs=$1
rq3_inside=$2
rq3_selection=$3
mount --make-rprivate /
mount -t proc proc "$rq3_fs/proc"
mount --bind /dev "$rq3_fs/dev"
chroot "$rq3_fs" /usr/bin/env -i HOME=/root LANG=C PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin LD_LIBRARY_PATH=/opt/rq3-maple-legacy/lib:/workdir/PERIOD/clang+llvm/lib PYTHONPATH=/opt/rq3-maple-legacy/python PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 RQ3_EXTRA_SELECTION="$rq3_selection" timeout -k 30s 10800s python3 "$rq3_inside/run-five-extra-formal.py" /workdir/rq3-cross-family-screen-o5n8qz
NS
