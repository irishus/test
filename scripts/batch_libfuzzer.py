'''THIS IS THE NEW SCRIPT'''

from ast import arg
from pathlib import Path
import subprocess
import os
import glob, shutil
import sys
import random

import re
from termios import TCIFLUSH
natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s)]

COVERAGE_PATH = os.path.join(os.getcwd(), "..", "coverage_command")

def HARDCODE_replace_target_dir(target_dir):
    return target_dir.replace("/build/", "/build_libfuzzer/")

def get_coverage_command(covpath=COVERAGE_PATH):
    # print(covpath)
    cmdfile = open(covpath, 'r')
    clean_cmd = HARDCODE_replace_target_dir(cmdfile.readline().strip())
    measure_cmd = HARDCODE_replace_target_dir(cmdfile.readline().strip())
    cmdfile.close()
    return clean_cmd, measure_cmd

def n_last_lines(path, n):
    with open(path, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines][-n:]

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

def write_to_file(filename, insts, allow_fail=False, log_progress=100, write_covcmd=False):
    clean_cmd, measure_cmd = get_coverage_command()
    with open(filename, 'w') as cfile:
        print('#!/bin/bash', file=cfile)
        print('echo ">> [START] $(date)"', file=cfile)
        print(clean_cmd, file=cfile)
        if not allow_fail:
            print('set -euo pipefail\n', file=cfile)
        if log_progress > 0:
            n_inst = len(insts)
            print('echo ">> [PROGRESS] 0/{} Test cases : $(date)"'.format(n_inst), file=cfile)
            for i, inst in enumerate(insts):
                inst = inst.lstrip('// ')
                print(inst, file=cfile)
                if ((i + 1) % log_progress == 0):
                    print('echo ">> [PROGRESS] {}/{} Test cases : $(date)"'.format((i+1), n_inst), file=cfile)
        else:
            for inst in insts:
                inst = inst.lstrip('// ')
                print(inst, file=cfile)
        print(measure_cmd, file=cfile)
        print('echo ">> [DONE] $(date)"', file=cfile)
    make_executable(filename)

REPLACE_TIMEOUT_CMD = r"timeout \d+s"
REPLACE_MAXTOTALTIME = r"-max_total_time=\d+"

def combine_instruction(tcdir, lffuzz_timeout=60):
    scrname = tcdir
    if tcdir == "all":
        tcdir = "."
    compile_cmds = []
    run_cmds = []
    repl_cmds = []
    abs_tcdir = os.path.join(os.getcwd(), tcdir)
    new_timeout_cmd = "timeout {}s".format(lffuzz_timeout)
    new_maxtotaltime = "-max_total_time={}".format(lffuzz_timeout)
    valids = [x for x in os.listdir(abs_tcdir) if '.cpp' in x]
    valids = sorted(valids, key=natsort)
    for name in valids:
        path = os.path.join(abs_tcdir, name)
        lines = n_last_lines(path, 8)
        compile_cmds.extend(lines[-2:])
        repl_cmds.extend([lines[-5]])
        new_run_cmd = re.sub(REPLACE_TIMEOUT_CMD, new_timeout_cmd, lines[-8])
        new_run_cmd = re.sub(REPLACE_MAXTOTALTIME, new_maxtotaltime, new_run_cmd)
        run_cmds.extend([new_run_cmd])
    
    compile_file = "tst_compile_{}_{}.sh".format(tcdir, lffuzz_timeout)
    run_file = "tst_run_{}_{}.sh".format(tcdir, lffuzz_timeout)
    replay_file = "tst_replay_{}_{}.sh".format(tcdir, lffuzz_timeout)

    write_to_file(compile_file, compile_cmds)
    write_to_file(run_file, run_cmds, allow_fail=True, write_covcmd=True)
    write_to_file(replay_file, repl_cmds, allow_fail=True, write_covcmd=True)
    print('DONE!', compile_file, run_file, replay_file)

def execute_cmd(cmd, store_output=False):
    cwd = os.getcwd()
    proc = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if not store_output:
        exit_code = proc.wait(30)
        return []

    output = []
    with proc.stdout:
        for line in iter(proc.stdout.readline, b''):
            line = line.decode("utf-8")
            line = line.rstrip()
            output.append(line)
    exit_code = proc.wait(30)
    return output

def usage():
    print('To use: python3 batch_libfuzzer.py [gen TC TIME]')
    
    print('TC determines which script is created [1|3|6|12|24|all]')
    print('1 means generate script for test cases in folder 1 (i.e., test cases generated in the first 1 hour)')
    print('')
    print('TIME is the timeout for libfuzzer in seconds (e.g., 60 means run libfuzzer for 1 minutes')
    print('Minimum 30 seconds')
    exit(0)

AVAILABLE_TC = ["1", "3", "6", "12", "24"]
if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        usage()

    cmd = args[1]
    if cmd == 'gen':
        if len(args) < 4:
            usage()
        test_case_dir = args[2]
        libfuzz_to = int(args[3])
        print(test_case_dir, libfuzz_to)
        assert(libfuzz_to >= 10)
        if test_case_dir.lower() == "all":
            # "all" means run all the generated test case with libfuzzer
            combine_instruction(".", libfuzz_to)
        elif test_case_dir in AVAILABLE_TC:
            # this means run the test case only in a specific folder
            combine_instruction(test_case_dir, libfuzz_to)
        else:
            usage()
    else:
        usage()
