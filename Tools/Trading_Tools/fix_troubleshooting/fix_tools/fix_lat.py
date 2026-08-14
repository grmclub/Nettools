import sys,os,getopt
import errno,traceback
import re
from datetime import *
import csv

def print help():
     print """

Mkt,session,clordid,ord_time,ack_time,delay

49,35,11,39,52,100

"""
sys.exit(1)


def percentile_calc(N,percent):
     if not N:
         return None
      k =len(N) * percent
      return N[int(k-1)]

def calc_latency(session,sess_list):
     
    sess_list.sort()
    p50 = percentile_calc(sess_list,0.50)
    p80 = percentile_calc(sess_list,0.80)
    p90 = percentile_calc(sess_list,0.90)
    p95 = percentile_calc(sess_list,0.95)
    p99 = percentile_calc(sess_list,0.99)
    pmax = len(sess_list) -1
    print("Session,Data_Size,50,80,90,95,99,Max")
    print("%s,%d,%s,%s,%s,%s,%s,%s" %(session,len(sess_list),p50,p80,p90,p95,p99,sess_list[pmax]))

def process_file():
    id_dict     = {}
    session_set = set()
    mkt_set     = set()

    with open(data_file, "r") as ifile:
        reader = csv.reader(ifile):
        for row in reader:
            session    = row[0].replace('"','')
            msgtype    = row[1]
            clordid    = row[2]
            ord_status = row[3]
            tnx_time   = row[4]
            market     = row[5]

            if msgtype == "D":
                 id_dict[clordid]={"sess":session, "t1": tnx_time, "t2":"", "time_diff":"", "mkt":market}
                 session_set.add(session)
                 mkt_set.add(market)
            else:
                if msgtype == "8":
                    if (ord_status =="0" || ord_status =="8"):
                        if id_dict.get(clordid):
                            id_dict[clordid] = tnx_time
                            t1 = datetime.datetime.strptime(id_dict[clordid]["t1"],"%Y%m%d-%H:%M:%S.%f").strftime("%s.%f")
                            t2 = datetime.datetime.strptime(id_dict[clordid]["t2"],,"%Y%m%d-%H:%M:%S.%f").strftime("%s.%f")
                            delay = abs(float(t2) - float(t1))
                            id_dict[clordid]["time_diff"] = "0.6f" % delay
    mkt_list ={}
    print("Mkt,Session,Clordid,Ord_time,Ack_time,Delay")
    for mkt in mkt_set:
        for sess in session_set:
            for key in id_dict.keys():
                if id_dict[key]["mkt"] == mkt and id_dict[key]["sess"] == sess:
                    id = id_dict[key] 
                    print('%s,%s,%s,%s,%s,%s" %(mkt,sess,key,id["t1"],id["2"],id["time_diff"]))
                    td=id_dict[key]["time_diff"]
                    key = mkt + "-" + sess
                    if mkt_list.get(key):
                        mkt_list[key].append(td)
                    else:
                        mkt_list[key] =[td]

    print("SESSION,SAMPLE,SIZE,MEDIAN,80,90,95,99,MAX")
    for session_list in sorted(mkt_list.keys()):
        cac_latency(session_list,mkt_list[session_list])

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h")
    except getopt.GetoptError as e:
        print e
        sys.exit()

    try:
        DATA_FILE = ""
        for o,a in opts:
            if o == "-f":
                DATA_FILE = a
            if o == "-h":
                printHelp()
                sys.exit(0)

        process_file(DATA_FILE)

    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print("Error: %s\n" % str(err))
        sys.exit(2)

if __name__ == "__main__":
    main()
