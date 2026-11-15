#!/bin/bash
set -eu
mkdir -p /home/qiuyang/sctbench-data
docker rm -f period-sctbench >/dev/null 2>&1 || true
docker run -d --privileged --name period-sctbench \
  --mount type=bind,source=/home/qiuyang/sctbench-data,target=/experiment-data \
  period:latest sleep infinity
docker cp /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/scripts/container_inspect.sh \
  period-sctbench:/tmp/container_inspect.sh
docker exec period-sctbench sed -i 's/\r$//' /tmp/container_inspect.sh
docker exec period-sctbench bash /tmp/container_inspect.sh
