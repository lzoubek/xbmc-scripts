#!/bin/env python


import urllib2,cookielib,base64,traceback,json,os,optparse,sys,datetime, shutil
from urllib import urlencode
from operator import itemgetter, attrgetter
def update_fields(item,fields):
	for field in fields:
		if not field in item:
			item[field]=''
	return item
class TestClient(object):
	def __init__(self):
		pass
	def get_movies(self):
		data = {}
		data['movies'] = []
		data['movies'].append({'rating': 9.99, u'movieid': 539, 'label': 'Movie', 'genre': 'Comedy / Romance', 'file': '/path/to/Movie.avi', 'year': 2011, 'duration': 1370})
		data['movies'].append({'rating': 4.99, u'movieid': 539, 'label': 'Movie 2', 'genre': 'Romance', 'file': '/path/to/Movie 2 ripped by someone.avi', 'year': 2000, 'duration': 2402})
		data['movies'].append({'rating': 9.99, u'movieid': 540, 'label': 'Another Movie', 'genre': 'Comedy', 'file': '/path/to/Another Movie.avi', 'year': 2011, 'duration': 3370})
		return data
	def get_recently_added_movies(self):
		data = {}
		data['movies'] = []
		data['movies'].append({'rating': 9.99, u'movieid': 539, 'label': 'Movie', 'genre': 'Comedy / Romance', 'file': '/path/to/Movie.avi', 'year': 2011, 'duration': 300})
		return data
	def get_tv_shows(self):
		data = []
		data.append({'count': 3, 'rating': '8.80', 'year': 2011, 'genre': u'Comedy', 'label': u'Serie 1'})
		data.append({'count': 10, 'rating': '9.80', 'year': 2000, 'genre': u'Comedy', 'label': u'Serie 2'})
		return data

class RPCClient(object):
	def __init__(self,uri,user,password):
		self.uri=uri
		self.user=user
		self.password=password
		
	def _request(self,data):
		request = urllib2.Request(self.uri,data)
		if not self.user == None:
			base64string = base64.encodestring('%s:%s' % (self.user, self.password))[:-1]
			authheader =  "Basic %s" % base64string
			request.add_header("Authorization", authheader)
		try:
			response = urllib2.urlopen(request)
			data = response.read()
			response.close()
			return self._decode(data)
		except urllib2.HTTPError, e:
			print 'Error getting response from %s'%self.uri
			print e.headers
			traceback.print_exc()
		except:
			print 'Error getting response from %s'%self.uri
			traceback.print_exc()
			
	def _decode(self,data):
		return json.loads(data.decode('utf-8','ignore'))['result']
	def _get_params(self):
		return ' ,\"params\": {\"fields\" :[\"rating\",\"year\",\"genre\",\"duration\"]}'
	def get_movies(self):
		return self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetMovies\", \"id\":1'+self._get_params()+'}')
		
	def get_recently_added_movies(self):
		return self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetRecentlyAddedMovies\", \"id\":1'+self._get_params()+'}')
	def get_tv_shows(self):
		data = []
		for show in  self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetTVShows\", \"id\":1'+self._get_params()+'}')['tvshows']:
			update_fields(show,['rating','year','genre'])
			showid = str(show['tvshowid'])
			seasons = self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetSeasons\",\"params\":{\"tvshowid\":'+showid+'}, \"id\":1})')
			update_fields(seasons,['seasons'])
			data.append({'label':show['label'],'count': len(seasons['seasons']),'rating':'%.2f'%show['rating'],'year':show['year'],'genre':show['genre']})
		return data

