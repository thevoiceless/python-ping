#! /usr/bin/env python

# NOTE: This was written to work with Python 2.4

import optparse, socket, sys, random, struct, time, select


# Type 8, Code 0 is an echo request
HEADER_MSG_TYPE = 8
HEADER_MSG_CODE = 0
# Wait up to 15 seconds for a response
TIMEOUT = 15


# 16-bit one's complement of the one's complement sum of the message, starting
# with the Type field
# Based on https://gist.github.com/pklaus/856268
def checksum(s):
	sum = 0

	# Go up to the highest even number less than or equal to the length
	upTo = 2 * (len(s) / 2)
	count = 0
	while count < upTo:
		val = ord(s[count]) + (ord(s[count + 1]) * 256)
		sum += val
		count += 2
	# If the string was of odd length, pad with one octet of zeros
	# See http://tools.ietf.org/html/rfc792
	if upTo < len(s):
		sum += ord(s[len(s) - 1])

	sum = (sum >> 16) + (sum & 0xffff)
	sum = sum + (sum >> 16)
	# Bitwise inversion
	result = ~sum
	result = result & 0xffff
	# Swap bytes for some reason
	result = result >> 8 | (result << 8 & 0xff00)

	return result


def buildHeader(check, packetID, seq):
	# Type field is 8 bits
	header = struct.pack('b', HEADER_MSG_TYPE)
	# Code fields is 8 bits
	header += struct.pack('b', HEADER_MSG_CODE)
	# Checksum field is 16 bits
	header += struct.pack('H', socket.htons(check))
	# Identifier field is 16 bits
	header += struct.pack('H', packetID)
	# Sequence number field is 16 bits
	header += struct.pack('h', seq)

	return header


def pingFiveTimes(hostIP):
	print "Ping %s five times..." % hostIP

	# We can build the packet once and send it 5 times because nothing changes
	# The ID probably should, but it doesn't matter here since we wait either
	# a response or a timeout before sending again
	packetID = random.randrange(65535)
	# Build dummy ICMP header with no checksum and sequence number 1
	dummyHeader = buildHeader(0, packetID, 1)
	# Checksum is based on the header and the data, but there is no data
	check = checksum(dummyHeader)
	# Build the actual header (which is really the whole packet)
	packet = buildHeader(check, packetID, 1)

	# Create the socket
	# NOTE: This requires superuser privileges
	try:
		# The correct protocol is chosen automatically for normal socket modes,
		# but we specify the ICMP protocol since we're opening a raw socket
		sock = socket.socket(socket.AF_INET,
			socket.SOCK_RAW,
			socket.getprotobyname('icmp'))
	except socket.error, (errno, msg):
		print >> sys.stderr, "Error creating ICMP socket:", msg
		sys.exit(errno)

	# Send the packet 5 times
	numReceived = 0
	minTime = sys.maxint
	maxTime = -1
	totalTime = 0.0
	for i in range(5):
		sendPacket = packet
		while sendPacket:
			# The sendto() function expects an address tuple that specifies a
			# port, but ICMP doesn't use a port so just tell it 1
			# Returns the number of bytes sent
			sentBytes = sock.sendto(sendPacket, (hostIP, 1))
			sendPacket = sendPacket[sentBytes:]

		timeSent = time.time()
		# The first three parameters to the select() function are, in this order,
		# lists of objects to:
		#   1. Wait on until ready to read from
		#   2. Wait on until ready to write to
		#   3. Wait on until an "exception condition occurs"
		# The last parameter is an optional timeout value in seconds
		response = select.select([sock], [], [], TIMEOUT)
		timeReceived = time.time()
		elapsedTime = timeReceived - timeSent
		if elapsedTime == 0:
			print "Warning: Elapsed time is zero, which may indicate that this \
			system cannot provide time with a better precision than 1 second"
		# Empty lists are returned if the timeout was reached
		if response[0] == []:
			print "Packet %i timed out" % (i + 1)
			continue

		data, addr = sock.recvfrom(1024)
		# Skip over the 20-byte IP header to get the 8-byte ICMP header
		header = data[20:28]
		pType, pCode, pCheck, pID, pSeq = struct.unpack('bbHHh', header)
		# Not sure if checking the ID is necessary, but we do it anyway
		if pID == packetID:
			numReceived += 1
			if elapsedTime > maxTime:
				maxTime = elapsedTime
			if elapsedTime < minTime:
				minTime = elapsedTime
			totalTime += elapsedTime

	# Stop here if we didn't get any responses
	if numReceived == 0:
		print "Got no responses"
		return
	# Otherwise, report stats
	minTime *= 1000
	maxTime *= 1000
	avgTime = (totalTime / numReceived) * 1000
	print "Min: %.2f ms\nMax: %.2f ms\nAverage: %.2f ms" % (minTime, maxTime, avgTime)


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
	except socket.gaierror, e:
		print >> sys.stderr, 'Could not resolve hostname', hostname
		sys.exit(1)

	hostIP = hostInfo[0][4][0]
	pingFiveTimes(hostIP)


# __name__ will be '__main__' if this code is being run directly (i.e. 'python dug.py')
# If so, execute normally. Otherwise, this code is being imported into another module
if __name__ == '__main__':
	main()
