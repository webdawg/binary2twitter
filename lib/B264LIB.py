#!/usr/bin/python

import base64
import binascii
import hashlib
import fileinput

#generates byte code from file for manipulation later on
def bytes_from_file(filename):
    with open(filename, "rb") as f: #Openfile read binary
        while True:
            byte = f.read(1)
            if not byte:
                break
            yield(byte)

def lines_from_file(filename):
    with open(filename, "r") as f: #Openfile read line
        while True:
            line = f.readline()
            if not line:
                break
            yield(line)


# indata = Source Binary File
# outdata = Output Binary File for checksum matching
# outhex = Hexed output file with Twitter Output Lines/Messages


def file_to_twitter_hex_file(indata,outhex):
	sha512summy = hashlib.sha512()
	sha_sum_output_file = open( "%s.sha512sum" % (outhex), 'w')
	twitter_hex_output_file = open(outhex, 'w') #Open Output Hex Message file for Twitter Output
	#Remove support for SHA sum in hex file source as I do not want to rewrite entire file.
	#twitter_hex_output_file.write("-SHASUMPLACEMENT-\n")
	total_twitter_message_count = 0 # Define total twitter message counter
	message_complete = 0 # Define counter for internal for loop binary joins
	byte_stuff = bytearray() # Set the byte_stuff array used to gather binary data
	for bytes_out in bytes_from_file(indata): #pull bytes_out by calling definition bytes_from_file
		if message_complete <= 66 and message_complete != 0: # Joins majority of data but skips if nothing there
			bytes_stuff = b''.join([bytes_stuff, bytes_out]) # Append new bytes to current bytes
			message_complete = message_complete + 1 # Increment loop joined
		if message_complete == 0: # Begins a new bytes_stuff arrary if none started
			bytes_stuff = bytes_out
			message_complete = message_complete + 1 # Increments join loop
		if message_complete == 67: # Ends join loop completing message
			hexwrite = binascii.b2a_hex(bytes_stuff) #convert bytes to hex for twitter message
			hexwrite_ascii = ascii(hexwrite) #Converts hex data type to ascii in prep for twitter hex output
			hexwrite_ascii = hexwrite_ascii[2:] # Removes b' data from conversion
			hexwrite_ascii = hexwrite_ascii[:-1] # Removes trailing ' from conversion
			print (hexwrite_ascii) #Print as TEST
			twitter_hex_output_file.write(hexwrite_ascii + "\n") #Write ascii hex output to hex output file and add a line
			print (len(hexwrite_ascii + "\n")) #Print Length of ascii
			total_twitter_message_count = total_twitter_message_count + 1 #increment hex twitter message count
			message_complete = 0 # set to 0 to start new read loop
		sha512summy.update(bytes_out)
	else:
		hexwrite = binascii.b2a_hex(bytes_stuff) #Same as above but catch a leftover unfinished output loop
		hexwrite_ascii = ascii(hexwrite)
		hexwrite_ascii = hexwrite_ascii[2:]
		hexwrite_ascii = hexwrite_ascii[:-1]
		print (hexwrite_ascii)
		twitter_hex_output_file.write(hexwrite_ascii + "\n")
		total_twitter_message_count = total_twitter_message_count + 1
		print ("Twitter messages generated:  ", total_twitter_message_count) #Print total twitter hex messages
		print ("END Binary to Twitter Message Hex Conversion")
		print ("SHA512SUM:  ",sha512summy.hexdigest())
		sha_sum_output_file.write(sha512summy.hexdigest() + "\n")
		

def print_twitter_hex(inhex):
	for lines_out in lines_from_file(inhex):
#		print ("Hex Lines: " + lines_out)
		print ("Hex Messages: ",lines_out)
		print ("Binary: ",binascii.a2b_hex(lines_out[:-1]))


def twitter_hex_2_binary(inhex,outputfile):
	output_object = open(outputfile,'wb')
	for lines_out in lines_from_file(inhex):
		output_object.write(binascii.a2b_hex(lines_out[:-1]))

#Replace Matching Line in file with
def search_and_replace(infile,search,replace):
	for line in fileinput.input(infile, inplace=True): 
		changed_line = line.replace(search, replace)
		print (changed_line[:-1])
		#if line == changed_line:
		#	print (line[:-1])
		#if line != changed_line:
		#	print (changed_line[:-1])
		#	fileinput.close()
#add_sha512sum_thex("twittertext.hex","-SHASUMPLACEMENT-","elite")

#file_to_twitter_hex_file(SourceData, OutputDest, OutputDestTwitterHex)
#twitter_hex_2_binary(OutputDestTwitterHex,Reconstructed_Twitter_Object)