#!/bin/bash
set -eu
docker start period-sctbench >/dev/null
echo "=== COMMIT ==="
docker exec period-sctbench git -C /workdir/PERIOD rev-parse HEAD
echo "=== IMAGE ID ==="
docker image inspect period:latest --format '{{.Id}}'
echo "=== REPODIGESTS ==="
docker image inspect period:latest --format '{{json .RepoDigests}}'
echo "=== REGISTRY DIGEST ==="
TOKEN=$(curl -fsSL "https://auth.docker.io/token?service=registry.docker.io&scope=repository:wcventure/period:pull" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')
curl -sI -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
  https://registry-1.docker.io/v2/wcventure/period/manifests/stable | tr -d '\r' | awk 'BEGIN{IGNORECASE=1} /^docker-content-digest:|^HTTP\//'
mkdir -p /home/qiuyang/sctbench-data/sctbench/scripts
sed -i 's/\r$//' /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/scripts/run_sctbench.py
sed -i 's/\r$//' /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/manifest.json
cp /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/scripts/run_sctbench.py /home/qiuyang/sctbench-data/sctbench/scripts/run_sctbench.py
cp /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/manifest.json /home/qiuyang/sctbench-data/sctbench/manifest.json
docker exec period-sctbench python3 /experiment-data/sctbench/scripts/run_sctbench.py /experiment-data/sctbench/manifest.json --pilot
