#!/bin/env python

import traceback,os,optparse,sys,client

def update_fields(item,fields):
	for field in fields:
		if not field in item:
			item[field]=''
	return item


usage="""%prog [options]

Goes through all movies in XBMC library and searches for movies contatined more than once. 
Files considered as duplicates are printed.

"""
parser = optparse.OptionParser(usage=usage)
parser.add_option('-u','--username',dest='username',default=None,help='authentication user')
parser.add_option('-p','--password',dest='password',default=None,help='authentication password')
parser.add_option('-s','--source',dest='source',default='http://localhost:8080/jsonrpc',help='source URI of XBMC [default=%default]')
(options,args) = parser.parse_args()

reader = client.RPCClient(options.source,options.username,options.password)
print 'Getting movies'
data = reader.get_movies()
if data == None:
	sys.exit(1)
print 'Done'
print 'Duplicates:'
try:
	movies = {}
	found = False
	for movie in data['movies']:
		movie = update_fields(movie,['label','file'])
		if movie['label'] in movies:
			movies[movie['label']].append(movie['file'])
		else:
			movies[movie['label']]=[movie['file']]
	for movie in movies:
		if len(movies[movie])>1:
			found = True
			print movie
			for file in movies[movie]:
				print ' '+file
	if not found:
		print 'Your library does not contain duplicate movies'
except:
	traceback.print_exc()
	sys.exit(1)
