#!/usr/bin/env python
##########################################################################
# HTTPreq - HTTP User Benchmark                                          #
# version 0.1                                                            #
# Copyright (c) Daniele Vona <danielv99@yahoo.it                         #
#                                                                        #
# This program is free software; you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation; either version 2 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
##########################################################################

import httplib
import time
import sys
import optparse
import re
import os
import commands
import random
from datetime import datetime
import threading

appname = "HTTPreq"
appver = "0.1"
deftime = 5   # Default timeout 5 sec
forceExit = None

# THREAD Function #
def doRequest(i,hostname,url,verbose,gnuplot):
	global forceExit
	request = []
	if (verbose): print "Start thread %.2d.." % i
	while 1:
		start_tottime = time.time()
		for uri in url:
			if (forceExit):
				return
			uri = uri.strip()
			u = uri.split("|")
			if (verbose): print " - Waiting %s sec and request URL: %s ..." % (u[3], u[2]),
			time.sleep(int(u[3]))
			starttime = time.time()
			try:
				host = httplib.HTTPConnection(hostname)
				host.putrequest("GET",u[2])
				host.putheader("User-Agent","HTTPreq/0.1")
				host.endheaders()
			except:
				if (verbose): print "Unable to connect %s" % hostname
				sys.exit(255)
			r1 = host.getresponse()
			if (r1.status != 200):
				print "Error: %s" % r1.reason
				return
			data1 = r1.read()
			endtime = time.time()
			avgtime = endtime - starttime
			request.append(avgtime)
			if (verbose): print "Request Time: %.3f sec" % (avgtime)
			loadavg=commands.getoutput("cat /proc/loadavg|awk '{ print $1 }'")
			if (gnuplot):
				fgnuplot = open(gnuplot, "a")
				fgnuplot.write(str(i)+" "+str(threading.activeCount())+" "+str(loadavg)+" "+str(avgtime)+"\n")
				fgnuplot.close()
			if avgtime > deftime:
				print "Thread %d exit with response time > default time: %f sec > %f sec." % (i, avgtime, deftime)
				host.close()
				forceExit = True
		end_tottime = time.time()
	if (verbose): print "Request Time for thread %d: %f sec: " % (i, end_tottime-starttime)

# HTTP BENCHMARK Function #
def httpbenchmark():
	global forceExit
	stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	hostname = options.hostname
	filename = options.filename
	t = []
	print "%s v%s - Copyright (c) 2009 Daniele Vona - License under GPLv2" % (appname, appver)
	if (options.verbose):
		print "Starting connection to %s." % hostname
		print "Date: %s ..." % stime
		print "Reading URLs from file %s ..." % filename
	f = open(filename, "r")
	url = f.readlines()
	f.close()
	start = time.time()
	print "Starting thread ..."
	for i in range(int(options.nthread)):
		t.append(threading.Thread(target=doRequest, args=(i,hostname,url,options.verbose,options.gnuplot)))
		t[i].start()
		time.sleep(random.random())
	print "All Thread started."
	print "Total Thread running: %d" % threading.activeCount()
	end = time.time()
	try:
		while 1:
			if (forceExit):
				sys.exit(0)
			pass
	except:
		forceExit = True

# LOG ANALYZE Function #
def loganalyze():
	print "%s v%s - Copyright (c) 2009 Daniele Vona - License under GPLv2" % (appname, appver)
	if (options.verbose): print "Log Analyzer."
	fin = open(options.filename, "r")
	fout = open("urls.txt", "w")
	l = []
	try:
		dt = None
		for line in fin:
			line = line.strip()
			m = re.split("(\s+)",line)
			m[0] = m[0].strip()
			m[6] = m[6].strip()
			d = datetime.strptime(m[6], "[%d/%b/%Y:%H:%M:%S")
			if dt is None:
				dt = d
			dt = d - dt
			m[12] = m[12].strip()
			ds = ((dt.days * 86400) + dt.seconds)
			if int(ds) < 0:
				ds = 0
			fout.write(m[0]+"|"+str(d)+"|"+m[12]+"|"+str(ds)+"\n")
			dt = d
	finally:
		fin.close()
		fout.close()
	print "Writed urls.txt file..."

# MAIN #
if __name__ == "__main__":
	usage = "Usage: %prog [-v] [-g file] <-A|-B> -f <file> [-H <host>] [-t <thread>]"
	parser = optparse.OptionParser(usage)
	parser.add_option('-H', '--host', dest='hostname', help='The host of the web server (default=localhost)', default='localhost', action='store')
	parser.add_option('-g', '--gnuplot', dest='gnuplot', help='Print output into a GNUPlot compatible file', action='store')
	parser.add_option('-t', '--thread', type='int', dest='nthread', help='Number of active thread (parallelism) (default=1)', default='1', action='store')
	parser.add_option('-f', '--file', dest='filename', help='Input file that contains user requests', action='store')
	parser.add_option('-A', dest='analyze', help='Analyze Access Log from file', action='store_true')
	parser.add_option('-B', dest='benchmark', help='Running HTTP benchmark throw host', action='store_true')
	parser.add_option('-v', dest='verbose', help='More Output', action='store_true')
	options, args = parser.parse_args()
	if options.filename is None:
		parser.error('Input file is required')
	if (options.gnuplot):
		f = open(options.gnuplot, "w")
		f.write("# HTTPreq Gnuplot Output\n")
		f.write("# (thread) (thread attivi) (load average) (request time)\n")
		f.close()
	if (options.analyze):
		loganalyze()
	elif (options.benchmark):
		httpbenchmark()
	else:
		parser.error('Action in required')

