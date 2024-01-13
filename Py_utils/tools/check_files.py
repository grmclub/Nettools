#!/usr/bin/env python

#import os, sys, getopt
import os, sys, getopt
import errno, traceback
import subprocess
import datetime
import global

def execCmd(cmd):
    #print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output,error) = p.communicate()
    ret = p.returncode
    output = output.strip()
    return(output, error, ret)
    
    
def send_mail(status.body):
    MAIL_SUB = "[" + status +"] ENV XXX Status"
    HEADER   = "Hi All"
    FOOTER   = "\n\nRegards,\n XXX Support"
    MAIL_TO  = "xxx@yyy.com"
    cmd      = ("echo -e \"%s\n\n%s\n%s" | mailx -s \"%s\" \"%s"" % ( HEADER, body, FOOTER, MAIL_SUB, MAIL_TO))
    #output, x,y = execCmd(cmd)
    execCmd(cmd)
    
def size_alert(infile, max_size):
    curr_size = os.path.getsize(infile)
    max_size = int(max_size)
    if curr_size >= max_size):
        body = ("File %s size: %d exceeds max_threshold: %d bytes" % (infile, curr_size, max_size))
        send_mail("ALERT", body)
    
def gen_date(days_before):
        day = (datetime.datetime.now() - datetime.timedelta(days_before))
        return (datetime.datetime.strftime(day, "%Y%m%d"))
        
        
def process_file(dir, file_pattern):
    day_of_week = datetime.datetime.today().weekday() #Monday is 0
    days_before = 1
    if day_of_week == 0:
        days_before =3
        
    dt = gen_date(days_before)
    pattern = file_pattern.replace('#DT#',dt)
    
    filepath = os.path.join(dir, pattern)
    file= glob.glob(fiepath)
    
    if not(file):
        msg = "File not delivered" + filepath
        print(msg)
        send_mail("NG", msg)
    else:
        print("File delivered: %s" % (file[0]))
        

def printHelp():
    print """Usage: %s -d <dir_to_check> -p <filename_pattern>

    OPTIONS:
         -d  dir to check
         -p  pattern of filename <'BB_#DT#*.csv'
         -h  Display this help message.
    """ % os.path.basename(__file__)  # sys.argv[0]



def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:p:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_PATH = "/home/user/dir/"
        FILE_PATTERN ="XXX_#DT#*.csv"
        for o,a in opts:
            if o == "-d":
                DATA_PATH = a
            if o == "-p":
                FILE_PATTERN = a                
            if o == "-h":
                printHelp()
                sys.exit(0)

        process_file(DATA_PATH, FILE_PATTERN)

    except Exception, err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" %str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()