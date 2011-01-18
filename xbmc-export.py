#!/bin/env python
import urllib2,cookielib,base64,traceback,json,os,optparse,sys,datetime, shutil
from urllib import urlencode
from operator import itemgetter, attrgetter

HTML=""" 
<html>
<head>
	<script type="text/javascript" src="tabber.js"></script> 
	<script type="text/javascript" src="jquery.tools.js"></script> 
	<script type="text/javascript" src="sortable.js"></script> 
	<link rel="stylesheet" type="text/css" href="tabber.css" />
</head>
<body>
	<p>Generated %s</p>
	<div class="tabber"> 
		<div class="tabbertab">
		<h1>All movies</h1>
		<table class="sortable" id="all-movies">
		<thead>
		<tr>
			<th>Index</th>
			<th>Name</th>
			<th>Year</th>
			<th>Genre</th>
			<th>File</th>
		</tr>
		<thead>
		<tbody>
		%s
		</tbody>
		</table>
		</div>
		<div class="tabbertab"> 
    	        <h1>Recently added  movies</h1> 
		<table class="sortable" id="recent-movies">
		<thead>
		<tr>
			<th>Index</th>
			<th>Name</th>
			<th>Year</th>
			<th>Genre</th>
			<th>File</th>
		</tr>
		<thead>
		<tbody>
		%s
		</tbody>
		</table>

		</div>
		<div class="tabbertab">
		<h1>Series</h1>
		<table class="sortable" id="series">
		<thead>
		<tr>
			<th>Index</th>
			<th>Name</th>
			<th>Seasons</th>
		</tr>
		<thead>
		<tbody>
		%s
		</tbody>
		</table>

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
	<td>%s</td>
	<td>%s</td>
</tr>
"""
TVSHOW="""
<tr>
	<td>%i</td>
	<td><strong>%s</strong></td>
	<td>%s</td>
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
	def _get_params(self):
		return ' ,\"params\": {\"fields\" :[\"rating\",\"year\",\"genre\",\"duration\"]}'
	def get_movies(self):
		return self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetMovies\", \"id\":1'+self._get_params()+'}')
		
	def get_recently_added_movies(self):
		return self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetRecentlyAddedMovies\", \"id\":1'+self._get_params()+'}')
	def get_tv_shows(self):
		data = []
		for show in  self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetTVShows\", \"id\":1})')['tvshows']:
			showid = str(show['tvshowid'])
			seasons = self._request('{\"jsonrpc\": \"2.0\", \"method\": \"VideoLibrary.GetSeasons\",\"params\":{\"tvshowid\":'+showid+'}, \"id\":1})')
			data.append({'label':show['label'],'count': len(seasons['seasons'])})
		return data
def filter_for_link(string):
	return string.replace('\"','')
def csfd_link(moviename,title):
	moviename = filter_for_link(moviename)
	return  """<a target="_blank" href="%shttp://csfd.cz/hledani-filmu-hercu-reziseru-ve-filmove-databazi/?search=%s">%s</a>"""%(ANONYM_TO,moviename,title)

def imdb_link(moviename,title):
	moviename = filter_for_link(moviename)
	return  """<a target="_blank" href="%shttp://www.imdb.com/find?s=all&q=%s">%s</a>"""%(ANONYM_TO,moviename,title)
def link(moviename):
	return '%s (%s) (%s)'%(moviename,csfd_link(moviename,'CSFD'),imdb_link(moviename,'IMDB'))

def update_fields(item,fields):
	for field in fields:
		if not field in item:
			item[field]=''
	return item

def parse_movies(data,sort=True):
	movies = []
	if sort:
		data['movies'] = sorted(data['movies'],key=itemgetter('label'))
	for movie in data['movies']:
		movie = update_fields(movie,['year','genre','file','label'])
		m = MOVIE % (len(movies)+1,link(movie['label']),movie['year'],movie['genre'],os.path.basename(movie['file']))
		movies.append(m)
	return movies
def parse_series(data):
	series = []
	data = sorted(data,key=itemgetter('label'))
	for show in data:
		s = TVSHOW % (len(series)+1,link(show['label']),show['count'])
		series.append(s)
	return series

ANONYM_TO='http://anonym.to/?'
usage='%prog [options]'
parser = optparse.OptionParser(usage=usage)
parser.add_option('-o','--output',dest='output',default='.',metavar='DIR',help='write output to DIR')
parser.add_option('-u','--username',dest='username',default=None,help='authentication user')
parser.add_option('-p','--password',dest='password',default=None,help='authentication password')
parser.add_option('-s','--source',dest='source',default='http://localhost:8080/jsonrpc',help='source URI of XBMC [default %default]')
parser.add_option('-a','--anonymize',dest='anonymize',action='store_true',default=False,help='enable anonymizing links via http://anonym.to')
(options,args) = parser.parse_args()
if not os.path.exists(options.output):
	print 'Output dir %s does not exist!'%options.output
	sys.exit(1)
if not options.anonymize:
	ANONYM_TO=''
print 'Getting movies'
reader = RPCClient(options.source,options.username,options.password)
movies = reader.get_movies()
if movies == None:
	sys.exit(0)
print 'Getting recently added'
recent_movies = reader.get_recently_added_movies()
print 'Getting shows'
tv_shows = reader.get_tv_shows()

try:
	print 'Writing output to %s' % options.output
	f = open(options.output+'/index.html','w')
	movies = parse_movies(movies)
	recent_movies = parse_movies(recent_movies,sort=False)
	tv_shows = parse_series(tv_shows)
	html = HTML % (datetime.datetime.now().strftime('%d. %m. %y at %H:%M:%S'),''.join(movies),''.join(recent_movies),''.join(tv_shows))
	f.write(html.encode('ascii','ignore'))
	print 'Done'
	print 'Copying resources'
	shutil.copy(RESOURCES+'resources/sortable.js',options.output)
	shutil.copy(RESOURCES+'resources/arrow-up.gif',options.output)
	shutil.copy(RESOURCES+'resources/arrow-down.gif',options.output)
	shutil.copy(RESOURCES+'resources/arrow-none.gif',options.output)
	shutil.copy(RESOURCES+'resources/tabber.js',options.output)
	shutil.copy(RESOURCES+'resources/tabber.css',options.output)
	shutil.copy(RESOURCES+'resources/jquery.tools.js',options.output)
	print 'Done'
except:
	traceback.print_exc()
f.close()
