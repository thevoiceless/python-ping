#! /usr/bin/env python

import optparse
import socket
import sys

def main():
	# Check command-line args for hostname
	parser = optparse.OptionParser(description = 'Ping in Python',
		usage = "usage: %prog hostname")

	(options, args) = parser.parse_args()
	if len(args) != 1:
		parser.error("Wrong number of arguments")
	hostname = args[0]

	# Try to resolve the IP of the host
	try:
		hostInfo = socket.getaddrinfo(hostname, 80)
	except socket.gaierror as e:
		print >> sys.stderr, 'Could not resolve hostname', hostname
		sys.exit(1)
	else:
		hostIP = hostInfo[0][4][0]
		print hostIP


# __name__ will be '__main__' if this code is being run directly (i.e. 'python dug.py')
# If so, execute normally. Otherwise, this code is being imported into another module
if __name__ == '__main__':
	main()