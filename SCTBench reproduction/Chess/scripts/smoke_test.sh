#!/bin/bash
set -u
export ROOT_DIR=/workdir/PERIOD
cd "$ROOT_DIR/test/doubleFree"
echo "=== BUILD doubleFree $(date -Is) ==="
./cleanDIR.sh
./build.sh
echo "BUILD_EXIT:$?"
echo "=== RUN -y -d 3 $(date -Is) ==="
python3 "$ROOT_DIR/tool/DBDS/run_PDS.py" -y -d 3 ./df
echo "RUN_EXIT:$?"
echo "=== ERROR FILES ==="
find out_df_1/Errors -type f | sort
ERR=$(find out_df_1/Errors -type f | sort | head -1)
echo "FIRST_ERR:$ERR"
if [ -n "$ERR" ]; then
  echo "=== REPLAY $(date -Is) ==="
  python3 "$ROOT_DIR/tool/DBDS/run_PDS.py" -r "$ERR" ./df
  echo "REPLAY_EXIT:$?"
fi
echo "=== SMOKE DONE $(date -Is) ==="
