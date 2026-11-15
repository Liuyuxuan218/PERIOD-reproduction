#!/bin/bash
set -u
echo "===OS==="
cat /etc/os-release
echo "===UNAME==="
uname -a
echo "===GCC==="
gcc --version | head -1
echo "===G++==="
g++ --version | head -1
echo "===CLANG==="
clang --version | head -2
echo "===LLVM==="
llvm-config --version
echo "===PY==="
python3 --version
python --version
echo "===NUMPY==="
python3 -c 'import numpy; print(numpy.__version__)'
echo "===SYSV==="
python3 -c 'import sysv_ipc; print(getattr(sysv_ipc, "__version__", "present"))' || true
pip3 show sysv_ipc | sed -n '1,4p'
echo "===MAKE CMAKE==="
make --version | head -1
cmake --version | head -1
echo "===SCHED==="
chrt -m || true
echo -n "sched_rt_runtime_us="
cat /proc/sys/kernel/sched_rt_runtime_us || true
echo
echo -n "nproc="
nproc
echo "===CPU==="
grep -m1 'model name' /proc/cpuinfo || true
echo "===MEM==="
free -h
echo "===HASH run_PDS==="
sha256sum /workdir/PERIOD/tool/DBDS/run_PDS.py
echo "===EVAL==="
ls /workdir/PERIOD/evaluation
echo "===ROOT==="
id
echo "===CAP==="
cat /proc/1/status | grep -E 'CapEff|CapBnd' || true
