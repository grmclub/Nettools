# -*- coding: utf-8 -*-
import os
import sys
import shutil
import getopt
import errno

import contextlib
import csv
import glob
import subprocess
import zipfile

def execCmd(cmd):
    print (cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ret = p.returncode
    return (ret, output, err)

def readcsv(filename):
    with open(filename, 'r') as ifile:
        reader = csv.reader(ifile)
        for row in reader:
            yield row

def readFile(filename):
    with open(filename, 'r') as ifile:
        for line in ifile:
            yield line

#--Check functions----------------------------------------------------------
def fileExists(filename):
    return os.path.isfile(filename)

def isFileEmpty(filename):
    return (os.stat(filename).st_size == 0)

def dirExists(dirname):
    return os.path.isdir(dirname)

def chkExists(fullPath):
    return os.path.exists(fullPath)

#--Dir Functions--------------------------------------------------------------
def createDir(dirpath):
        os.mkdir(dirpath)

def moveDir(src_dir, dst_dir):
    try:
        os.rename(src_dir,dst_dir)
    except OSError as err:
        if err.errno != errno.ENOENT: # no such file or directory
            raise OSError("%s: Error: %s" % sys._getframe().f_code.co_name,err)

def removeDirTree(dirpath):
    try:
        shutil.rmtree(dirpath)
    except OSError as err:
        if err.errno != errno.ENOENT: # no such file or directory
            raise OSError("%s: Error: %s" % sys._getframe().f_code.co_name,err)

#--File functions---------------------------------------------------------------
def makeSymLink(src, dst):
    try:
        os.symlink(src, dst) #Create a symbolic link pointing to src named dst
    except OSError as err:
        if err.errno != errno.ENOENT: # no such file or directory
            raise OSError("%s: Error: %s" % sys._getframe().f_code.co_name,err)

def makeTmpFile():
    return os.tmpnam()

def listFiles(dirname, rexp):
    try:
        os.chdir(dirname)
        files = glob.glob(rexp)
        return files
    except OSError as err:
        if err.errno != errno.ENOENT: # no such file or directory
            raise OSError("%s: Error: %s" % sys._getframe().f_code.co_name,err)

def copyFile(src, dst):
    try:
        shutil.copyfile(src, dst)
    except (OSError, shutil.Error) as e:
        raise IOError("%s: Error: %s" %(sys._getframe().f_code.co_name,  e.strerror))

def moveFile(src_file, dst_file):
    try:
        shutil.move(src_file,dst_file)
    except (OSError, shutil.Error) as e:
        raise IOError("%s: Error: %s" %(sys._getframe().f_code.co_name,  e.strerror))

def moveSelectedFiles(src_path, dst_path, rexp):
    try:
        os.chdir(src_path)
        files = glob.glob(rexp)
        for filename in files:
            shutil.move(filename, dst_path + filename)
    except (OSError, shutil.Error) as e:
        raise IOError("%s: Error: %s" %(sys._getframe().f_code.co_name,  e.strerror))

def removeFiles(rm_path, rexp):
    try:
        os.chdir(rm_path)
        files = glob.glob(rexp)
        for filename in files:
            os.unlink(filename)
    except OSError as err:
        if err.errno != errno.ENOENT: # no such file or directory
            raise OSError("%s: Error: %s" % sys._getframe().f_code.co_name,err)

def getAccessTime(filepath):
    return os.stat(filepath).st_mtime
    
def getLatestFile(filepath):
    try:
        list_of_files = glob.glob(filepath) ## Filename can be specified with regex pattern
        latest_file = max(list_of_files, key=os.path.getmtime)
        return latest_file
    except OSError as err:
        if err.errno != errno.ENOENT: # no such file or directory
            raise OSError("%s: Error: %s" % sys._getframe().f_code.co_name,err)

#--File archive functions----------------------------------------------------------
def archive(data_dir,today):
	cmd=”cd %s;zip -r %s.zip *.%s*.csv” %(data_dir,today,today)
	result,e,r = execCmd(cmd)

def archiveFiles(arch_filename, src_path):
    arch_dir = os.path.dirname(arch_filename)
    src_dir  = os.path.dirname(src_path)
    src_file = src_path

    if os.path.isfile(src_path):
        src_file = os.path.basename(src_path)

    if chkExists(arch_dir):
        cmd = "tar -C %s -czvf %s %s" % (src_dir, arch_filename, src_file)
        (ret,out,err) = execCmd(cmd)

        if (ret != 0):
            raise IOError("%s: Error: %s" % (sys._getframe().f_code.co_name, err))
    else:
        raise IOError("%s: Error: Path error %s" % (sys._getframe().f_code.co_name, arch_dir))

def extract_zip_archive(src_archive_path, dst_path):
    with contextlib.closing(zipfile.ZipFile(src_archive_path, "r")) as zip_ref:
        zip_ref.extractall(dst_path)
        
def cleanup_files(data_dir):
    day_of_week = datetime.today().isoweekday() #Monday is 1
        days_before = 7
    if day_of_week == 1:
            days_before =10
    #data_dir=”/home/xx/yy/data”
    cmd=”find %s -type f -mtime +%d -delete” %(data_dir,days_before)
    result,e,r = execCmd(cmd)
    print result

#--Remote file functions-----------------------------------------------------------
def upload_to_hosts(rhost_list, rlogin, src_file_path, dst_path, timeout=10):
    for rhost in rhost_list:
        upload(rhost, rlogin, src_file_path, dst_path, timeout)

def upload(rhost, rlogin, src_file_path, dst_path, timeout=10):
        cmd = "rsync -avP --timeout %d %s %s@%s:%s" % (timeout, src_file_path, rlogin, rhost, dst_path)
        (ret,out,err) = execCmd(cmd)

        if (ret != 0):
            raise IOError("%s: Error: %s" % (sys._getframe().f_code.co_name, err))

def download(rhost, rlogin, src_file_path, dst_path, timeout=10):
        cmd = "rsync -avP --timeout %d %s@%s:%s %s" % (timeout, rlogin, rhost, src_file_path, dst_path)
        (ret,out,err) = execCmd(cmd)

        if (ret != 0):
            raise IOError("%s: Error: %s" % (sys._getframe().f_code.co_name, err))

def listRemoteFile(host, user, dirpath):
    cmd = "ssh %s@%s \"ls -l %s|awk '{print \$9}'|sort\"" % (user, host, dirpath)
    (ret,out,err) = execCmd(cmd)

    if (ret != 0):
        raise IOError("%s: Error: %s" % (sys._getframe().f_code.co_name, err))
    return out

def delRemoteFile(user, host, filename):
        cmd = "ssh %s@%s \"rm -f %s\"" % (user, host, filename)
        (ret,out,err) = execCmd(cmd)

        if (ret != 0):
            raise IOError("%s: Error: %s" % (sys._getframe().f_code.co_name, err))
            
#--Shell mail Functions--------------------------------------------------------------
def send_file(from_addr,to_addr,cc,sub,body,filename):
	cmd = """ echo \"%s\"| mailx -s \"%s\" -r \"%s\" -c \"%s\" -a %s %s """ %(body,sub,from_addr,cc,fiilename,to_addr)
	result,e,r = execCmd(cmd)

def send_html_mail(sub,body,from_addr,to_addr):
	#from_addr="xx@yahoo.com"
	#to_addr="xx@yahoo.com"
	#today = datetime.datetime.now().strftime("%Y%m%d")
	#sub ="XXX Report for %s" %(today)
	cmd = """
	(
	echo "To: %s"
	echo "From: %s"
	echo "Subject: %s"
	echo "Mime-version: 1.0"
	echo "Content-Type: text/html; charset='utf-8'"
	echo
	echo "%s"
	) | /usr/sbin/sendmail -t """ %(to_addr,from_addr,sub,body)
	result,e,r = execCmd(cmd)
	print "Mail send done"
