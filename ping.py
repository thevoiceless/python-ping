#! /usr/bin/env python

import optparse

def main():
	parser = optparse.OptionParser(description = 'Ping in Python',
		usage = "usage: %prog hostname")

	(options, args) = parser.parse_args()
	if len(args) != 1:
		parser.error("Wrong number of arguments")


if __name__ == '__main__':
	main()