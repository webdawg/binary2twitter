#!/usr/bin/python

#MultiVar Example: 	output_message = ("SETOUTPUTSTART_%d_%d" % (total_messages_ah,number_of_hex))
#max hex = 4095

import lib.B264LIB as B264LIB
import binascii
import hashlib


#output sha512sum of file
def sha512sum_file(fin):
	f = open(fin, "rb")
	sha512summy = hashlib.sha512()
	test = 1
	while True:
		data = f.read(128)
		if not data:
			break
		test += 1
		sha512summy.update(data)
	print(sha512summy.hexdigest())
	print(test)

#Get number of Lines From a File
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

#Increments ABC Loop for message matching checksum
def abcloopinc(abcin):
	if ord(abcin) == 122:
		out = chr(ord('a'))
		return out
	else:	
		out = chr(ord(abcin)+1)
		return out

#The max header message count is 3 chars
#but in the format all 3 chars need to be in use
#this takes a hex value, converts it to ascii, and
#ouputs a min of 3 ascii chars
def format_hex_count(hin):
	hex_message_count_ascii = ascii(hin)
	hex_message_count_ascii = hex_message_count_ascii[3:]
	hex_message_count_ascii = hex_message_count_ascii[:-1]
	if len(hex_message_count_ascii) < 2:
		hex_message_count_ascii = ("00%s" % hex_message_count_ascii)
	if len(hex_message_count_ascii) < 3:
		hex_message_count_ascii = ("0%s" % hex_message_count_ascii)
	return hex_message_count_ascii


#twitter_hex_2_message_file("twitter.hex","twitter.hex.messages","9dsfj09ds","w00t.odt")
def twitter_hex_2_message_file(inhexfile,outputmessagefile,sha512sum,filename):
	number_of_hex = file_len(inhexfile)
	twitter_message_file = open(outputmessagefile, 'w')
	print ("Number of Data Lines to Process:  ",number_of_hex)
	total_messages_ah = number_of_hex + 2
	#This creates the standard header that we can search for in a stream
	#for begining of a filetype message wich also includes total number
	#of messages not including itself, but including the sum header and filename header
	#no post ID included in this definition
	output_message = ("TDSENC__SETOUTPUTSTART_%d" % (total_messages_ah))
	print (output_message)
	twitter_message_file.write(output_message + "\n")
	message_count = 1
	hex_message_count = format_hex_count(hex(message_count))
	print (hex_message_count)
	output_message = ("S|%s|H|%s" % (hex_message_count,sha512sum))
	print (output_message)
	twitter_message_file.write(output_message + "\n")
	message_count += 1
	hex_message_count = format_hex_count(hex(message_count))
	output_message = ("F|%s|%s" % (hex_message_count,filename))
	print (output_message)
	twitter_message_file.write(output_message + "\n")
	checksum = "a"
	for lines_out in B264LIB.lines_from_file(inhexfile):
		message_count += 1
		if message_count == 4096:
			message_count = 1
		hex_message_count = format_hex_count(hex(message_count))
		line_constructed = ("D|%s%s%s" % (hex_message_count,checksum,lines_out))
		twitter_message_file.write(line_constructed)
		checksum = abcloopinc(checksum)


#Turns sorted twitter messages into twitter hex and if None pulls filename from
#file itself if not specified
def message_file_2_binary(inmessagefile,outfile):
	line_number = 1
	filename_created = 0
	for lines_out in B264LIB.lines_from_file(inmessagefile):
		if line_number == 4 and filename_created == 0:
			if outfile is None:
				print("File header missing and you have given no filename output\n")
				print("please specify one via command line or check input file.\n")
				break
			else:
				filename = outfile
				output_object = open(filename,'wb')
				print("Filename set to:  ", filename)
		if 'TDSENC__SETOUTPUTSTART_' in lines_out:
			print("File Header Found on Line:  ", line_number)
		if 'S|' in lines_out:
			print("Sum Header Found on Line:  ", line_number)
			sha512sum = lines_out[8:-1]
			print("SHA512SUM:  ", sha512sum)
			datum_type = lines_out[6:]
			datum_type = datum_type[:1]
			if datum_type == "H":
				print("Sum header states HEX data")
		if 'F|' in lines_out:
			print("Filename Header Found on Line:  ", line_number)
			if outfile is None:
				filename = lines_out[6:]
				filename = filename[:-1]
				filename_created = 1
				output_object = open(filename,'wb')
				print("Filename set to:  ", filename)
		if 'D|' in lines_out:
			print("Datum Header Found on Line:  ", line_number)
			hex_line = lines_out[6:]
			hex_line = hex_line[:-1]
			print(hex_line)
			output_object.write(binascii.a2b_hex(hex_line))
		line_number += 1



#message_file_2_binary("twitter.hex.messages",None)
#message_file_2_binary("twitter.hex.messages","output.odt")
#sha512sum_file("output.odt")