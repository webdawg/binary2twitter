#!/usr/bin/env python

#only one binary mode can be selected

import argparse
import struct
import lib.B264LIB as B264LIB
import lib.headers as headers
import lib.twitter_write as twitter_write

parser = argparse.ArgumentParser(description='Data into the twitter stream.')

parser.add_argument('-t2b','--TwitterToBinary', action='store_true',help="Perform Twitter Message To Binary File Conversion From InputFile")
parser.add_argument('-b2t','--BinaryToTwitter', action='store_true',help="Perform Binary To Twitter Message File Conversion From InputFile")
parser.add_argument('-h2b','--HexToBinary', action='store_true',help="Convert Raw Hex Lines to Binary")
parser.add_argument('-tt','--TwitterTake', action='store_true',help="Pull Twitter Messages and Store in OutputFile")
parser.add_argument('-tl','--TwitterLoad', action='store_true', help="Output Twitter Messages to Twitter")
parser.add_argument('-md','--MessageDelay', default=5, type=int)
parser.add_argument('-d', '--debug', help="Set debug value if you are having problems", default=0, type=int, choices=range(1,3))
parser.add_argument('-i', '--InputFile',help="Input Files")
parser.add_argument('-o', '--OutputFile',help="Output Files")

args = vars(parser.parse_args())


#Debug Code
if args['debug'] is True:
	print(parser.parse_args(),  "\n")

#Twitter messages to binary
if args['TwitterToBinary'] == True:
	if args['InputFile'] is None:
		print ("Error:  No Twitter message input file given!")
		exit()
	if args['OutputFile'] is None:
		print ("Warning:  No Binary File output destination given")
		print ("Will try to pull from .messages file")
		#exit()
	print (".messages To Binary Selected")
	print ("Input .messages File:  ", args['InputFile'])
	print ("Ouput Binary File:  ", args['OutputFile'])
	headers.message_file_2_binary(args['InputFile'],args['OutputFile'])
	#B264LIB.twitter_hex_2_binary(args['InputFile'],args['OutputFile'])

#Just Hex to Binary
if args['HexToBinary'] == True:
	if args['InputFile'] is None:
		print ("Error:  No HEX input file given!")
		exit()
	if args['OutputFile'] is None:
		print ("Warning:  No Binary File output destination given")
		print ("Will try to pull from .messages file")
		#exit()
	print (".messages To Binary Selected")
	print ("Input .messages File:  ", args['InputFile'])
	print ("Ouput Binary File:  ", args['OutputFile'])
	headers.message_file_2_binary(args['InputFile'],outfile)
	#B264LIB.twitter_hex_2_binary(args['InputFile'],args['OutputFile'])

if args['BinaryToTwitter'] == True:
	if args['InputFile'] is None:
		print ("Error:  No Binary Input file given!")
		exit()
	if args['OutputFile'] is None:
		print ("Error:  No Twitter Hex output file destination given")
		exit()
	print ("Binary To Twitter Selected")
	print ("Input Binary File:  ", args['InputFile'])
	print ("Output Hex File:  ",args['OutputFile'])
	B264LIB.file_to_twitter_hex_file(args['InputFile'],args['OutputFile'])
	#for lines_out in lines_from_file("%s.sha512sum" % (args['OutputFile'])[:-1]):
	headers.twitter_hex_2_message_file(args['OutputFile'],"%s.messages" % (args['OutputFile']),(''.join(B264LIB.lines_from_file("%s.sha512sum" % (args['OutputFile'])))[:-1]),args['InputFile'])

if args['TwitterTake'] == True:
	print ("Twitter Take Selected")
	print (vars(parser.parse_args())['OutputFile'])
	
if args['TwitterLoad'] == True:
	print ("Twitter Load Selected")
	print (vars(parser.parse_args())['InputFile'])
	if args['BinaryToTwitter'] == False:
		#Need to add twitter parms
		twitter_write.importconfigtwitter(None,None,None,None,None)
		twitter_write.start_twitter()
		twitter_write.open_twitter_write(args['InputFile'],args['MessageDelay'])

#parser.print_help()


