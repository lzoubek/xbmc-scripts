#!/bin/env python

RESOURCES=''


import urllib2,cookielib,base64,traceback,json,os,optparse,sys,datetime, shutil, client
from urllib import urlencode
from operator import itemgetter, attrgetter

RESOURCES=os.path.dirname(os.path.abspath(__file__))


def update_fields(item,fields):
	for field in fields:
		if not field in item:
			item[field]=''
	return item


usage="""%prog [options]



"""
parser = optparse.OptionParser(usage=usage)
parser.add_option('-u','--username',dest='username',default=None,help='authentication user')
parser.add_option('-p','--password',dest='password',default=None,help='authentication password')
parser.add_option('-s','--source',dest='source',default='http://localhost:8080/jsonrpc',help='source URI of XBMC [default=%default]')
parser.add_option('-t','--test',dest='test',action='store_true',default=False,help='only tests connection and prints list of movies')
(options,args) = parser.parse_args()
if len(args) != 1:
	parser.error("Script needs exactly 1 argument")
	sys.exit(1)
if not os.path.exists(args[0]):
	print 'Output dir %s does not exist! '%args[0]
	sys.exit(1)

reader = client.RPCClient(options.source,options.username,options.password)
print 'Getting recently added movies'
data = reader.get_recently_added_movies()
line = '---------------------------------'
print 'Done'
try:
	for movie in data['movies']:
		data['size'] = 0
		movie = update_fields(movie,['label','file'])
		if movie['file'].startswith('stack://'):
			movie['file'] = movie['file'].replace('stack://','')
			movie['files'] = movie['file'].split(',')
		else:
			movie['files'] = [movie['file']]
		for file in movie['files']:
			file = file.strip()
			if os.path.exists(file):
				data['size'] += os.path.getsize(file)

	if options.test:
		print 'List of recently added movies'
		for movie in data['movies']:
			print line
			print (movie['label'])			
			for file in movie['files']:
				print ' - %s'% file
				if not os.path.exists(file):
					print '   WARN: File does not exist'
			print line
		print line
		print 'Total: %0.2f GB' % (data['size']/(1024*1024*1024.0))
		print line
	else:
		print 'Total size to be copied : %0.2f GB' % (data['size']/(1024*1024*1024.0))
		for movie in data['movies']:
			print 'Copying movie %s '% (movie['label'])			
			for file in movie['files']:
				if not os.path.exists(file):
					print '   WARN: File \'%s\' does not exist' % file
				else:
					dirname = os.path.dirname(file).split('/')[-1]
					dest = arg[0]+'/'+dirname
					print ' - Copying - %s to %s'% (file,dest)
					os.makedirs(os.path.dirname(dest))
					shutil.copy(file,dest)
				

#	shutil.copy(RESOURCES+'/resources/jquery.tools.js',options.output)

	print 'Done'
except:
	traceback.print_exc()
	sys.exit(1)
