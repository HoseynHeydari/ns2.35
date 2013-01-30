import os
import sys
from optparse import OptionParser
import subprocess
import matplotlib
if os.uname()[0] == 'Darwin':
    matplotlib.use('macosx')
import matplotlib.pyplot as p
import numpy

def runonce(fullname, proto, w, gateway, nsrc, type, simtime, on, off, outfname):
    global conffile
    gw = gateway
    if proto.find("XCP") != -1:
        sink = 'TCPSink/XCPSink'
        gw = 'XCP'              # overwrite whatever was given
    elif proto.find("Linux") != -1:
        sink = 'TCPSink/Sack1/DelAck'
    else:
        sink = 'TCPSink'

    if fullname.find("CoDel") != -1:
        gw = "sfqCoDel"

    if type == "bytes":
        runstr = './newremy.tcl %s -tcp %s -sink %s -gw %s -ontype %s -onrand %s -avgbytes %d -offrand %s -offtime %s -nsrc %d -simtime %d' % (conffile, proto, sink, gw, type, w, on, w, off, nsrc, simtime)
    else:
        runstr = './newremy.tcl %s -tcp %s -sink %s -gw %s -ontype %s -onrand %s -ontime %d -offrand %s -offtime %s -nsrc %d -simtime %d' % (conffile, proto, sink, gw, type, w, on, w, off, nsrc, simtime)                
    print runstr
    fnull = open(os.devnull, "w") 
    fout = open(outfname, "ab")
    output = subprocess.call(runstr, stdout=fout, stderr=fnull, shell=True)    
    return

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--conffile", type="string", dest="remyconf", 
                      default = "", help = "Remy config file (Tcl)") 
    parser.add_option("-d", "--dirresults", type="string", dest="resdir", 
                      default = "./tmpres", help = "directory for results")
    parser.add_option("-p", "--proto", type="string", dest="proto",
                      default = "TCP/Newreno", help = "protocol")
    parser.add_option("-t", "--type", type="string", dest="ontype",
                      default = "bytes", help = "by bytes or by seconds")
    (config, args) = parser.parse_args()

    if not os.path.exists(config.resdir):
        os.mkdir(config.resdir)

    conffile = config.remyconf

    simtime = 300
    maxsrcs = 32
    iterations = 5

    # protolist = ['TCP/Newreno', 'TCP/Linux/cubic', 'TCP/Linux/compound', 'TCP/Vegas', 'TCP/Reno/XCP', 'TCP/Newreno/Rational', 'Cubic/sfqCoDel']

    protolist = config.proto.split() # which transport protocol(s) are we using?
    onofftimes = [1, 5, 10]
#    avg_byte_list = [16000, 96000, 192000]
    avgbytes = 100000 # from Allman's March 2012 data and 2013 CCR paper
    worktypes = ['Pareto', 'Exponential']

    for proto in protolist:
        fullname = proto
        if proto == "Cubic/sfqCoDel":
            proto = "TCP/Linux/cubic"
        for wrk in worktypes:
            for onoff in onofftimes:
                numsrcs = 1
                while numsrcs <= maxsrcs:
                    for i in xrange(iterations):
                        if config.ontype == "bytes":
                            outfname = '%s/%s.%s.nconn%d.%son%d.off%d.simtime%d' % (config.resdir, fullname.replace('/','-'), wrk, numsrcs, config.ontype, avgbytes, onoff, simtime)
                            runonce(fullname, proto, wrk, 'DropTail', numsrcs, config.ontype, simtime, avgbytes, onoff, outfname)
                        else:
                            outfname = '%s/%s.%s.nconn%d.%son%d.off%d.simtime%d' % (config.resdir, fullname.replace('/','-'), wrk, numsrcs, config.ontype, onoff, onoff, simtime)
                            runonce(fullname, proto, wrk, 'DropTail', numsrcs, config.ontype, simtime, onoff, onoff, outfname)
                        print outfname
                    numsrcs = 2*numsrcs
