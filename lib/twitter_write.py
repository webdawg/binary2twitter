#!/usr/bin/python

import configparser
import sys
from twython import Twython, TwythonError
import pprint
import calendar
import time
from lib.debug import *
import os
import threading
import random
import lib.B264LIB as B264LIB

def importconfigtwitter(configfile,iapp_key,iapp_secret,ioauth_token,ioauth_token_secret):
	global app_key
	global app_secret
	global oauth_token
	global oauth_token_secret
	if iapp_key is not None:
		d1print("Setting app key from command line")
		app_key = iapp_key
	if iapp_secret is not None:
		d1print("Setting app secret from command line")
		app_secret = iapp_secret
	if ioauth_token is not None:
		d1print("Setting oauth token from command line")
		oauth_token = ioauth_token
	if ioauth_token_secret is not None:
		d1print("Setting oauth token secret from command line")
		oauth_token_secret = ioauth_token_secret
	if iapp_key is None or iapp_secret is None or ioauth_token is None or ioauth_token_secret is None:
		if configfile is None:
			print ("Using default config file binarytwitter.conf")
			configfilename = "binarytwitter.conf"
		else:
			print ("Config file specified...setting config file:",configfile)
			configfilename = configfile
		if os.path.isfile(configfilename) is False:
			print("Config file missing...aborting!")
			sys.exit()
		config = configparser.ConfigParser()
		config.read(configfilename)
		if 'TwitterSettings' in config:
			d1print ("Found Twitter Settings In Config")
			if "app_key" in config['TwitterSettings'] and iapp_key is None:
				d1print("Twitter app key set from config")
				app_key = config['TwitterSettings']['app_key']
			if "app_secret" in config['TwitterSettings'] and iapp_secret is None:
				d1print("Twitter app secret set from config")
				app_secret = config['TwitterSettings']['app_secret']
			if "oauth_token" in config['TwitterSettings'] and ioauth_token is None:
				d1print("Twitter oauth token set from config")
				oauth_token = config['TwitterSettings']['oauth_token']
			if "oauth_token_secret" in config['TwitterSettings'] and ioauth_token_secret is None:
				d1print("Twitter oauth token secret set from config")
				oauth_token_secret = config['TwitterSettings']['oauth_token_secret']
#		else:
	
#		elif:
	try:
		app_key
	except NameError:
		print("Twitter app key not found in config file and not specified on command line")
		print("Quitting")
		sys.exit()
	try:
		app_secret
	except NameError:
		print("Twitter app secret not found in config file and not specified on command line")
		print("Quitting")
		sys.exit()
	try:
		oauth_token
	except NameError:
		print("Twitter oauth token not found in config file and not specified on command line")
		print("Quitting")
		sys.exit()
	try:
		oauth_token_secret
	except NameError:
		print("Twitter oauth token secret not found in config file and not specified on command line")
		print("Quitting")
		sys.exit()
	d1print ("Twitter app key set to: %s" % ( app_key))
	d1print ("Twitter app secret set to: %s" % ( app_secret ))
	d1print ("Twitter oauth token set to: %s" % ( oauth_token ))
	d1print ("Twitter oauth token secret set to: %s" % ( oauth_token_secret ))


def start_twitter():
	global twitter
	twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

#bad connection?
def get_twitter_application_rate_limit():
	rate_limit_status = twitter.get_application_rate_limit_status()
	d3print ("RATE LIMIT STATUS MAINT DICT KEYS:")
	d3print (rate_limit_status.keys())
	if debug3(): print("ENTIRE RETURNED TWITTER APPLICATION RATE LIMIT STATUS DICT:")
	if debug3(): pprint.pprint(rate_limit_status)
	#Example of how to get keys out of dicts
	#pprint.pprint (rate_limit_status['resources']['application']['/application/rate_limit_status'].keys())
	app_calls_left = rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining']
	if debug2(): print ("Remaining Twitter Application Calls:",app_calls_left)
	#makes a call
	#print(twitter.get_home_timeline())
	#gets date inforation from header of last call
	d1print("Date pulled from Twitter HTTP Header:")
	d1print(twitter.get_lastfunction_header('date'))
	#prints human looking time
	#print(time.strftime(twitter.get_lastfunction_header('date')))
	twitter_time_last_call = time.strptime(twitter.get_lastfunction_header('date')[5:], "%d %b %Y %H:%M:%S %Z")
	if debug2(): print("Twitter time struct:\n",twitter_time_last_call)
	#04 Jan 2014 22:04:58
	twitter_time_last_call_epoch = calendar.timegm(twitter_time_last_call)
	if debug2(): print("Converted Twitter epoch Time:",twitter_time_last_call_epoch)
	app_calls_next_reset = rate_limit_status['resources']['application']['/application/rate_limit_status']['reset']
	if debug2(): print("Application Calls epoch reset:",app_calls_next_reset)
	app_calls_seconds_until_reset = app_calls_next_reset - twitter_time_last_call_epoch
	if debug2(): print("Number of seconds left until Application Call Reset:",app_calls_seconds_until_reset)
	#pull information from headers instead of actual output
	#print ("Current get_application_rate_limit_status Limit Ceiling:")
	#print (twitter.get_lastfunction_header('x-rate-limit-limit'))
	#print ("Number of get_application_rate_limit_status Requests Remaining:")
	#print (twitter.get_lastfunction_header('x-rate-limit-remaining'))
	#print ("epoch Time until get_application_rate_limit_status request reset:")
	#print (twitter.get_lastfunction_header('x-rate-limit-reset'))
	return app_calls_left, app_calls_seconds_until_reset

def twitter_engine(operation,data):
	if operation == "write":
		#Twitter has a max of 1000 tweets per day and is also broken
		#up into additional undocumented time increments.  To prevent
		#spamming.  So our limits are 1000 a day which we have to guess
		#how many to post in a certian time increment and 180 application
		#api per 900 seconds.  900 seconds is what twitter has now and
		#we can pull this from returned twitter information.
		#We also want to keep track of this data out of application so we can
		#break the program and restart later if we want to.  That is, what
		#message we are on.
		#
		#This may be a waste of a API use but if the account is used somewhere else
		#it will make sure we do not hit limits
		global app_api_seconds_left
		global twitter_app_calls_left
		global twitter_between_message_limit
		if app_api_seconds_left == 0:
			time.sleep(twitter_between_message_limit)
			twitter_app_calls_left, api_call_till_reset_seconds = get_twitter_application_rate_limit()
			twitter_api_countdown(api_call_till_reset_seconds)
		global message_sent
		message_sent = 0
		while message_sent == 0:
			if twitter_app_calls_left > 0:
				time.sleep(twitter_between_message_limit)
				twitter.update_status(status='%s' % (data))
				if debug2: print("Twitter Status Updated:  %s" % (data))
				twitter_app_calls_left = twitter_app_calls_left - 1
				message_sent = 1
			else:
				if debug2 (): print("Sleeping for %s seconds for API call refresh." % (app_api_seconds_left))
				time.sleep(app_api_seconds_left + twitter_between_message_limit)
				twitter_app_calls_left, api_call_till_reset_seconds = get_twitter_application_rate_limit()
				twitter_api_countdown(api_call_till_reset_seconds)


def twitter_api_countdown(secondsleft):
	twitter_countdown_thread = threading.Thread(target=countdown,args=(secondsleft,))
	twitter_countdown_thread.start()

def countdown(seconds):
	twitter_counter_active = 1
	global app_api_seconds_left
	app_api_seconds_left = seconds
	while app_api_seconds_left is not 0:
		time.sleep(1)
		app_api_seconds_left = app_api_seconds_left - 1
		if debug3(): print("Twitter Application API Countdown:",app_api_seconds_left)
	twitter_counter_active = 0

#global twitter_between_message_limit
#twitter_between_message_limit = 5

global twitter_app_calls_left
twitter_app_calls_left = 0

global app_api_seconds_left
app_api_seconds_left = 0

global message_sent

def open_twitter_write(inputfile,messagedelay):
	#Need to keep track to see if entire message has been sent
	#Line Bla out of Bla
	
	
	#success lines written to twitterload file
	
	global twitter_between_message_limit
	global message_sent
	message_sent = 0
	twitter_between_message_limit = messagedelay
	twitterload_file = open( "%s.twitterload" % (inputfile), 'w')
	current_line = 0
	for lines_out in B264LIB.lines_from_file(inputfile):
		current_line = current_line + 1
		global line_sent
		line_sent = 0
		while line_sent == 0:
		
			if debug2():
				print("Attempting to Send A Message:")
				print("LINE:", current_line)
				print("Message:",lines_out)
			try:
				twitter_engine("write",lines_out)
				#Twitter has a max of 1000 tweets per day and is also broken
				#up into additional undocumented time increments.  To prevent
				#spamming.  So our limits are 1000 a day which we have to guess
				#how many to post in a certian time increment and 180 application
				#api per 900 seconds.  900 seconds is what twitter has now and
				#we can pull this from returned twitter information.
				#We also want to keep track of this data out of application so we can
				#break the program and restart later if we want to.  That is, what
				#message we are on.
				#
				#This may be a waste of a API use but if the account is used somewhere else
				#it will make sure we do not hit limits

			except TwythonError as e:
				the_string_error = str(e)
				print("Twython Error")
				if the_string_error.find("Caused by <class 'socket.gaierror'>: [Errno -2] Name or service not known") >= 0:
					print("Name or service not known...So connection issues to twitter")
				d3print("Full Error:")
				d3print(e)
				#global message_sent
				message_sent = 0
			#global message_sent
			if message_sent == 1:
				d2print("Message Sent Successfully!")
				twitterload_file.write( str(current_line).zfill(10) + "SUCCESS" + "\n" )
				line_sent = 1
			elif message_sent == 0:
				d2print("MESSAGE NOT SENT!  RETRYING")
			
			#if message is not sent, check limits, and delay further


def open_twitter_read():
	#none of this works for write
	#twitter wants to hide api status update limits
	print ("Current Write Limit Ceiling:")
	print (twitter.get_lastfunction_header('x-rate-limit-limit'))
	print ("Number of Write Requests Remaining:")
	print (twitter.get_lastfunction_header('x-rate-limit-remaining'))
	print ("epoch Time until write request reset:")
	print (twitter.get_lastfunction_header('x-rate-limit-reset'))


#test writing twitter engine
#random.seed()
#importconfigtwitter(None,None,None,None,None)
#start_twitter()
#twitter_engine("write","TDEV %s" % (random.getrandbits(20)))
#twitter_engine("write","TDEV %s" % (random.getrandbits(20)))
#twitter_engine("write","TDEV %s" % (random.getrandbits(20)))


#start_twitter()
#get_twitter_rate_limits()
#open_twitter_write()


#gets inforation from header of last call
#twitter.get_lastfunction_header('access_token')
#open_twitter_write()
