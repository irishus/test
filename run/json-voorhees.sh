#!/bin/bash
set -euo pipefail

TARGET=build/clementine
TIMEOUT=$1
OUT_PREFIX=$2
SUBJ_DIR=$3

TRANS_UNIT=${SUBJ_DIR}/src/jsonv/all.cpp
OBJ_DIR=${SUBJ_DIR}/build/CMakeFiles/jsonv.dir/src/jsonv
SRC_DIR=${SUBJ_DIR}

ls ${TRANS_UNIT} > /dev/null
ls ${OBJ_DIR} > /dev/null
ls ${SRC_DIR} > /dev/null

MAX_DEPTH=2
XTRA_LD=""

${TARGET} ${TRANS_UNIT} \
  --obj-dir ${OBJ_DIR} \
  --src-dir ${SRC_DIR} \
  --max-depth ${MAX_DEPTH} \
  --fuzz-timeout ${TIMEOUT} \
  --xtra-ld "${XTRA_LD}" \
  --out-prefix ${OUT_PREFIX}