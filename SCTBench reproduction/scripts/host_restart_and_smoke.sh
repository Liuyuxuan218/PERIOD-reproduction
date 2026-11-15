#!/bin/bash
set -eu
docker start period-sctbench
sleep 1
docker inspect period-sctbench --format 'status={{.State.Status}} oom={{.State.OOMKilled}} err={{.State.Error}} exit={{.State.ExitCode}}'
docker cp /mnt/c/Users/LOQ/os/PERIOD-reproduction/SCTBench/scripts/smoke_test.sh period-sctbench:/tmp/smoke_test.sh
docker exec period-sctbench sed -i 's/\r$//' /tmp/smoke_test.sh
docker exec period-sctbench bash /tmp/smoke_test.sh
