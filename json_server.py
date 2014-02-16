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
import argparse
import struct
import lib.headers as headers
import lib.twitter_write as twitter_write
from PIL import Image
import urllib, os
import socketserver
import json
from flask import Flask, render_template, request, jsonify

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
	
importconfigtwitter(None,None,None,None,None)
twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

#image size 375x375





#class MyTCPServer(socketserver.ThreadingTCPServer):
#	allow_reuse_address = True
#
#class MyTCPServerHandler(socketserver.BaseRequestHandler):
#	def handle(self):
#		try:
#			data = json.loads(self.request.recv(1024).decode('UTF-8').strip())
#			# process the data, i.e. print it:
#			print(data)
#			print (data["message"])
#			print (data["link"])
#			url = data["link"]
#			filename = url.split('/')[-1].split('#')[0].split('?')[0]
#			print (filename)
#			os.system('wget %s' % (data["link"]))
#			photo = open(filename, 'rb')
#			twitter.update_status_with_media(status=str(data["message"]), media=photo)
#			# send some 'ok' back
#			self.request.sendall(bytes(json.dumps({'return':'ok'}), 'UTF-8'))
#		except Exception as e:
#			print("Exception wile receiving message: ", e)
#
#server = MyTCPServer(('107.150.57.51', 13373), MyTCPServerHandler)
#server.serve_forever()


# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def index():
	# Render template
	return render_template('index.html')

@app.route('/tweet', methods = ['GET'])
def get():
	# Get the parsed contents of the form data
	print (request.args.get('price'))
	print (request.args.get('pic_url'))
	descript = request.args.get('description')
	url = request.args.get('pic_url')
	the_message=request.args.get('price')
	filename = url.split('/')[-1].split('#')[0].split('?')[0]
	print (filename)
	os.system('wget %s' % (url))
	os.system('convert -rotate 270 %s %s' % (filename,filename))
	photo = open(filename, 'rb')
	twitter.update_status_with_media(status="@SWHNL #swhnl 4SALE: $%s | %s" %(the_message, descript), media=photo)
	return ("Recived: price, %s | pic_url, %s | description, %s" % (request.args.get('price'), request.args.get('pic_url'), request.args.get('description')))

# Run
if __name__ == '__main__':
    app.run(
        host = "0.0.0.0",
        port = 13373
    )


