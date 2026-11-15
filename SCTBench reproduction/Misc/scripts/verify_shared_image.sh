#!/bin/bash
set -eu
docker start period-sctbench >/dev/null
docker exec period-sctbench bash -lc 'set -eu
echo "=== GIT ==="
if [ -d /workdir/PERIOD/.git ]; then
  git -C /workdir/PERIOD rev-parse HEAD
  git -C /workdir/PERIOD log -1 --format="%H%n%ci%n%s"
  git -C /workdir/PERIOD status -sb
else
  echo "NO_GIT_DIR"
fi
echo "=== NUMPY ==="
python -c "import numpy; print(\"py2\", numpy.__version__)"
python3 -c "import numpy; print(\"py3\", numpy.__version__)"
echo "=== WLLVM ==="
python -c "import wllvm; print(\"py2-wllvm\", getattr(wllvm, \"__file__\", \"ok\"))" || true
python3 -c "import wllvm; print(\"py3-wllvm-ok\")" || true
echo "=== HASHES ==="
sha256sum \
  /workdir/PERIOD/evaluation/ConVul-CVE-Benchmarks/CVE-2009-3547/2009-3547.cpp \
  /workdir/PERIOD/evaluation/ConVul-CVE-Benchmarks/CVE-2011-2183/2011-2183.cpp \
  /workdir/PERIOD/evaluation/ConVul-CVE-Benchmarks/CVE-2016-7911/2016-7911.cpp \
  /workdir/PERIOD/tool/DBDS/run_PDS.py \
  /workdir/PERIOD/tool/init_env.sh
'
