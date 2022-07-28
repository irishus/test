# CLEMENTINE: C++ unit testing based on clever method sequence generation technique

## Introduction

CLEMENTINE is an implementation of Unit-level Testing for C++ based on random method call sequence generation. 

CLEMENTINE automatically generates test driver files for the target program `P`, 
each of which consists of various method calls of `P`.  
In addition, CLEMENTINE improves the test coverage of `P` further
by applying **libfuzzer** to change `P`’s state by mutating
arguments of the methods.

CLEMENTINE is a continuation of [CITRUS](https://github.com/swtv-kaist/CITRUS).

## Requirements

CLEMENTINE was tested running on Ubuntu 18.04. The requirements of CLEMENTINE are:
1. LLVM/Clang++ 11.0.1,
1. LCOV coverage measurement tool (we used a [modified LCOV](https://github.com/henry2cox/lcov/tree/diffcov_initial) for CLEMENTINE development),
1. CMake 3.15,
1. Python 3.

We provide a shell script to install all CLEMENTINE requirements. (**root privilege required**)
```shell
./scripts/dep.sh <path/to/install/directory>
```

## Build Instruction

To build CLEMENTINE is simply executing the build script
```shell
./scripts/build.sh
```
CLEMENTINE will be built in `build` directory.


## Building CLEMENTINE Subjects

We provide the target programs that are use in CITRUS experiment at 
`replication` directory. For simplicity, you can execute the following shell script (from the CLEMENTINE **root** project directory) to build all our experiments subjects.
```shell
./scripts/bootstrap.sh subjects             # to build in subjects dir
```

## Running CLEMENTINE Method Call Sequence Generation

Currently CLEMENTINE only supports command-line interface.
```shell
./build/CLEMENTINE ${TRANS_UNIT} \
  --obj-dir ${OBJ_DIR} \
  --src-dir ${SRC_DIR} \
  --max-depth ${MAX_DEPTH} \
  --fuzz-timeout ${TIMEOUT} \
  --xtra-ld "${XTRA_LD}" \
  --out-prefix ${OUT_PREFIX}
```
For easier usage, we recommend to write separate shell script(s) to configure the command-line arguments as demonstrated in `run` directory. For example, to run CLEMENTINE on `hjson` library:
```shell
./run/hjson.sh 43200 tc_hjson subjects/hjson-cpp          # 12 hours
```
where `tc_hjson` represents the target directory where the generated test cases will be put at, and `subjects/hjson-cpp` represents the `hjson` directory.

## Running CLEMENTINE libfuzzer

Currently the libfuzzer stage must be manually triggered after the method call sequence generation. CLEMENTINE writes the libfuzzer harness drivers in `out_libfuzzer` directory. Each driver has compilation instruction at the end of the file.

To ease the libfuzzer stage, we provide `batch_libfuzzer.py` script (i.e., CLEMENTINE already puts this script in `out_libfuzzer` directory) to collect all compilation, running, and test case replaying instructions for libfuzzer stage.
```shell
# Run below commands from out_libfuzzer directory

# generate the script to compile, run, and replay. 
python3 batch_libfuzzer gen 12 120
# 12 in the above command means generating test cases generated in the first 12 hours. (Available options : [1|3|6|12|24|all])
# 120 in the above command means running libfuzzer for each test case for 120 seconds. (minimum: 10 seconds)
# the python script will generate 3 script: tst_compile_12_120.sh, tst_run_12_120.sh, and tst_repl_12_120.sh

# compile all harness drivers
./tst_compile_12_120.sh

# Running libfuzzer
./tst_run_12_120.sh

# Replaying libfuzzer generated test cases
./tst_repl_12_120.sh
```

---
Developed by **SWTV Lab**, **KAIST**
