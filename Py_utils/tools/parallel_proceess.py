#!/usr/bin/env python

import os, sys, getopt
import errno, traceback
import subprocess
from multiprocessing import Process, Pool


def printHelp():
    print ("""Usage: %s -f <filename>

    OPTIONS:
         -f  host list file
         -h  Display this help message.
    """ % os.path.basename(__file__))

def execCmd(cmd):
    #print (cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (output,err,ret)


def parallel_run():
    tasks = []
    cmd_list = [ './xx.sh > xx ', './yy.sh > yy']
    for command in cmd_list:
        task = Process(target=execCmd, args=(command,))
        task.start()
        tasks.append(task)

    # Wait for tasks to complete
    for task in tasks:
        task.join()

def parallel_pool():
    cmd_list = [ './xx.sh > xx ', './yy.sh > yy']
    nprocs = 2 # nprocs is the number of processes to run
    ParsePool = Pool(nprocs)
    ParsePool.map(execCmd,cmd_list)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:H:h")
    except getopt.GetoptError as e:
        print(e)
        sys.exit()

    try:
        HOST_FILE  = ""
        HOST_LIST  = ""
        for o,a in opts:
            if o == "-f":
                HOST_FILE = a
            if o == "-H":
                HOST_LIST = a
            if o == "-h":
                printHelp()
                sys.exit(0)
        #parallel_run()
        parallel_pool()

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()

