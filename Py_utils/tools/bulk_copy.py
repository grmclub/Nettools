#!/usr/bin/env python

import os,sys,getopt
import errno, traceback
import subprocess 
from multiprocessing import Process, Pool
from datetime import *

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

class upload_dir:
    def __init__(self,DATA_DIR, REMOTE_DIR):
         self.remote_host = xx
         self.remote_dir = REMOTE_DIR
         self.cmd = "SCP -ro Compression=yes %s/* %s:%s" % (DATA_DIR, self.remote_host,REMOTE_DIR)
         self.cmd_list = []


      def parse_seq(self, folder_start,folder_end):
            start = int(folder_start)
            end = int(folder_end)
            cmd = self.cmd
            for folder in range(start,end+1):
                 xx = cmd.replace('#',str(folder))
                 self.cmd_list.append(xx)

       def parse_filelist(self, file_list):
           lines = ""
           cmd = self.cmd
           with open(file_list, "r") as ifile:
                lines = "".join(ifile.readlines())

            for folder in lines.split("\n"):
                   if folder == "":
                      continue 
                      #print (folder)
                  xx = cmd.replace('#',str(folder))
                 self.cmd_list.append(xx)

       def trigger_upload(self):
             nprocs =3
             pp = Pool(nprocs)
             results = pp.map(execCmd, self.cmd_list)
             pp.close()
             pp.join()

             for row in results:
                  print (row)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h")
    except getopt.GetoptError as e:
        print (e)
        sys.exit()

    try:
        FILE_LIST= ""
        DATA_DIR = ""
        REMOTE_DIR= ""
        FOLDER_START= ""
        FOLDER_END= ""

        for o,a in opts:
            if o == "-f":
                FILE_LIST = a
            if o == "-d":
                DATA_DIR = a
            if o == "-r":
                REMOTE_DIR = a
            if o == "-s":
                FOLDER_START = a
            if o == "-e":
                FOLDER_END = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        ud = upload_dir(DATA_DIR, REMOTE_DIR)
        if (FILE_LIST != ""):
             ud.parse_file(FILE_LIST)
        else:
             ud.parse_sequence(FOLDER_START, FOLDER_END)

         ud.trigger_upload()
       

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()
