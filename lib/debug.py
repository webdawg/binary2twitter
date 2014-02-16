#!/usr/bin/python

debug = 3
if debug <= 3:
	print ("Current Debug Level:",debug)

def d3print(pin):
	if debug >= 3 and debug is not 0: print(pin)

def d2print(pin):
	if debug >= 2 and debug is not 0: print(pin)

def d1print(pin):
	if debug >= 1 and debug is not 0: print(pin)

def debug1():
	if debug >= 1 and debug is not 0:
		return True
	else:
		return False

def debug2():
	if debug >= 2 and debug is not 0:
		return True
	else:
		return False

def debug3():
	if debug >= 3 and debug is not 0:
		return True
	else:
		return False