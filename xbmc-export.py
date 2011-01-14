#!/bin/env python
import urllib2,cookielib,base64,traceback,json,os,optparse,sys,datetime, shutil
from urllib import urlencode
from operator import itemgetter, attrgetter

HTML=""" 
<html>
<head>
	<script type="text/javascript" src="tabber.js"></script> 
	<script type="text/javascript" src="jquery.tools.js"></script> 
	<link rel="stylesheet" type="text/css" href="tabber.css" />
</head>
<body>
	<p>Generated %s</p>
	<div class="tabber"> 
		<div class="tabbertab">
		<h1>Recently added movies</h1>
		<table>%s</table>
		</div>
		<div class="tabbertab"> 
    	        <h1>All movies</h1> 
			<table>%s</table>
		</div>
		<div class="tabbertab">
		<h1>Series</h1>
			<table>%s</table>
		</div>
	</div>
</body>
</html>
"""
MOVIE="""
<tr>
	<td>%i</td>
	<td><strong>%s</strong></td>
	<td>%s</td>
</tr>
"""
TVSHOW="""
<tr>
	<td>%i</td>
	<td><strong>%s</strong></td>
	<td>%s seasons</td>
</tr>
"""
RESOURCES=''
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
	def get_movies(self):
		return self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetMovies\", \"id\":1})')
		
	def get_recently_added_movies(self):
		return self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetRecentlyAddedMovies\", \"id\":1})')
	def get_tv_shows(self):
		data = []
		for show in  self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetTVShows\", \"id\":1})')['tvshows']:
			showid = str(show['tvshowid'])
			seasons = self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetSeasons\",\"params\":{\"tvshowid\":'+showid+'}, \"id\":1})')
			data.append({'label':show['label'],'count': len(seasons['seasons'])})
		return data
def parse_movies(data):
	movies = []
	data['movies'] = sorted(data['movies'],key=itemgetter('label'))
	for movie in data['movies']:
		m = MOVIE % (len(movies)+1,movie['label'],os.path.basename(movie['file']))
		movies.append(m)
	return movies
def parse_series(data):
	series = []
	data = sorted(data,key=itemgetter('label'))
	for show in data:
		s = TVSHOW % (len(series)+1,show['label'],show['count'])
		series.append(s)
	return series
usage='%prog [options]'
parser = optparse.OptionParser(usage=usage)
parser.add_option('-o','--output',dest='output',default='.',metavar='DIR',help='write output to DIR')
parser.add_option('-u','--username',dest='username',default=None,help='authentication user')
parser.add_option('-p','--password',dest='password',default=None,help='authentication password')
parser.add_option('-s','--source',dest='source',default='http://localhost:8080/jsonrpc',help='source URI of XBMC [default %default]')
(options,args) = parser.parse_args()
print 'Getting movies'
reader = RPCClient(options.source,options.username,options.password)
movies = reader.get_movies()
if movies == None:
	sys.exit(0)
recent_movies = reader.get_recently_added_movies()
tv_shows = reader.get_tv_shows()

try:
	print 'Writing output to %s' % options.output
	f = open(options.output+'/index.html','w')
	movies = parse_movies(movies)
	recent_movies = parse_movies(recent_movies)
	tv_shows = parse_series(tv_shows)
	html = HTML % (datetime.datetime.now().strftime('%d. %m. %y at %H:%M:%S'),''.join(recent_movies),''.join(movies),''.join(tv_shows))
	f.write(html.encode('ascii','ignore'))
	print 'Done'
	print 'Copying resources'
	shutil.copy(RESOURCES+'resources/tabber.js',options.output)
	shutil.copy(RESOURCES+'resources/tabber.css',options.output)
	shutil.copy(RESOURCES+'resources/jquery.tools.js',options.output)
	print 'Done'
except:
	traceback.print_exc()
f.close()
