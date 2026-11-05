#!/usr/bin/env bash
# Run from the PERIOD repository root.
# Back up out_2016-7911_1 before running cleanDIR.sh.

set -euo pipefail
ROOT_DIR="${ROOT_DIR:-$PWD}"
BENCHMARK_DIR="$ROOT_DIR/evaluation/ConVul-CVE-Benchmarks/CVE-2016-7911"

if [[ ! -f "$ROOT_DIR/tool/init_env.sh" ]]; then
  echo "Run from the PERIOD repository root or set ROOT_DIR." >&2
  exit 1
fi

source "$ROOT_DIR/tool/init_env.sh"
cd "$BENCHMARK_DIR"

./cleanDIR.sh
clang -g -emit-llvm -c ./2016-7911.cpp -o 2016-7911.bc
"$ROOT_DIR/tool/staticAnalysis/staticAnalysis.sh" 2016-7911

export Con_PATH="$BENCHMARK_DIR/ConConfig.2016-7911"
"$ROOT_DIR/tool/staticAnalysis/DBDS-INSTRU/dbds-clang-fast++" \
  -g -fsanitize=address ./2016-7911.cpp \
  -o 2016-7911 -lpthread -ldl

"$ROOT_DIR/tool/DBDS/run_PDS.py" -d 3 ./2016-7911
