Ping in Python
=====

Description
-----
A simple version of the `ping` utility written in Python. It sends five ICMP echo requests to a given hostname and calculates the min, max, and average RTTs.

Usage (requires superuser privileges):
-----
`sudo python ping.py hostname`  
or  
`sudo ./ping.py hostname`

Notes
-----
* Requires superuser privileges to send the ICMP packets
* The code is written to work with Python 2.4