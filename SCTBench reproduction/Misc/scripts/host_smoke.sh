#!/bin/bash
set -eu
python3 - <<'PY'
import hashlib, subprocess
files = [
    "tool/DBDS/run_PDS.py",
    "tool/staticAnalysis/staticAnalysis.sh",
    "evaluation/CS/account/account_bad.c",
    "evaluation/CB/pbzip2-0.9.4/build.sh",
    "Dockerfile",
]
revs = ["b6f72a7b06d01ffa7114b640312873ec2578a5ea", "cb8deb9a176e5bb292d70d46557dd61dc0e98069"]
for f in files:
    print("FILE", f)
    for rev in revs:
        data = subprocess.check_output(["git", "-c", "safe.directory=/mnt/c/Users/LOQ/os/PERIOD", "-C", "/mnt/c/Users/LOQ/os/PERIOD", "show", f"{rev}:{f}"])
        print(rev[:12], hashlib.sha256(data).hexdigest())
PY
echo "=== CONTAINER HASHES ==="
docker exec period-sctbench bash -lc 'sha256sum /workdir/PERIOD/tool/DBDS/run_PDS.py /workdir/PERIOD/tool/staticAnalysis/staticAnalysis.sh /workdir/PERIOD/evaluation/CS/account/account_bad.c /workdir/PERIOD/evaluation/CB/pbzip2-0.9.4/build.sh /workdir/PERIOD/Dockerfile'
sed -i 's/\r$//' /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/scripts/smoke_test.sh
docker cp /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/scripts/smoke_test.sh period-sctbench:/tmp/smoke_test.sh
docker exec period-sctbench sed -i 's/\r$//' /tmp/smoke_test.sh
docker exec period-sctbench bash /tmp/smoke_test.sh
