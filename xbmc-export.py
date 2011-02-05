#!/bin/env python

RESOURCES=''


import urllib2,cookielib,base64,traceback,json,os,optparse,sys,datetime, shutil
from urllib import urlencode
from operator import itemgetter, attrgetter

RESOURCES=os.path.dirname(os.path.abspath(__file__))

HTML=""" 
<html>
<head>
	<meta name="generator" content="xbmc-export" />
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
			<th class="unsortable">Links</th>
			<th>Year</th>
			<th>Genre</th>
			<th>Rating</th>
			<th>Duration</th>
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
			<th class="unsortable">Links</th>
			<th>Year</th>
			<th>Genre</th>
			<th>Rating</th>
			<th>Duration</th>
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
			<th class="unsortable">Links</th>
			<th>Seasons</th>
			<th>Year</th>
			<th>Genre</th>
			<th>Rating</th>
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
	<td>%s</td>
	<td>%s</td>
	<td>%s</td>
	<td>%s</td>
</tr>
"""
class TestClient(object):
	def __init__(self):
		pass
	def get_movies(self):
		data = {}
		data['movies'] = []
		data['movies'].append({'rating': 9.99, u'movieid': 539, 'label': 'Movie', 'genre': 'Comedy / Romance', 'file': '/path/to/Movie.avi', 'year': 2011, 'duration': 1370})
		data['movies'].append({'rating': 4.99, u'movieid': 539, 'label': 'Movie 2', 'genre': 'Romance', 'file': '/path/to/Movie 2 ripped by someone.avi', 'year': 2000, 'duration': 2402})
		data['movies'].append({'rating': 9.99, u'movieid': 539, 'label': 'Another Movie', 'genre': 'Comedy', 'file': '/path/to/Another Movie.avi', 'year': 2011, 'duration': 3370})
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

def update_fields(item,fields):
	for field in fields:
		if not field in item:
			item[field]=''
	return item

class Generator(object):
	def __init__(self,anonymize=False,names=[],uris=[]):
		self.anonymize = ''
		if anonymize:
			self.anonymize = 'http://anonym.to?'
		self.services=[]
		for i in range(0,len(names)):
			self.services.append({'name':names[i],'uri':uris[i]})

	def filter_for_link(self,string):
		return string.replace('\"','')
	def _link(self,moviename,title,uri):
		moviename = self.filter_for_link(moviename)
		return  """<a target="_blank" href="%s%s%s">%s</a>"""%(self.anonymize,uri,moviename,title)
	def _get_links(self,moviename):
		links = []
		for service in self.services:
			links.append(self._link(moviename,service['name'],service['uri']))
			links.append(' ')
		return ''.join(links) 

	def parse_movies(self,data,sort=True):
		movies = []
		if sort:
			data['movies'] = sorted(data['movies'],key=itemgetter('label'))
		for movie in data['movies']:
			movie = update_fields(movie,['year','genre','file','label','rating','duration'])
			movie['rating'] = '%.2f' % movie['rating']
			movie['duration'] = '%i' % (int(movie['duration'])/60)
			m = MOVIE % (len(movies)+1,movie['label'],self._get_links(movie['label']),movie['year'],movie['genre'],movie['rating'],movie['duration'],os.path.basename(movie['file']))
			movies.append(m)
		return movies

	def parse_series(self,data):
		series = []
		data = sorted(data,key=itemgetter('label'))
		for show in data:
			s = TVSHOW % (len(series)+1,show['label'],self._get_links(show['label']),show['count'],show['year'],show['genre'],show['rating'])
			series.append(s)
		return series

usage="""%prog [options]

Example (generate results from localhost with anonymous links to CSFD movie db):
%prog -o /tmp -u xbmc -p xbmc -a -n CSFD -l http://www.csfd.cz/hledani-filmu-hercu-reziseru-ve-filmove-databazi/?search=
"""
parser = optparse.OptionParser(usage=usage)
parser.add_option('-o','--output',dest='output',default='.',metavar='DIR',help='write output to DIR')
parser.add_option('-u','--username',dest='username',default=None,help='authentication user')
parser.add_option('-p','--password',dest='password',default=None,help='authentication password')
parser.add_option('-s','--source',dest='source',default='http://localhost:8080/jsonrpc',help='source URI of XBMC [default=%default]')
parser.add_option('-l','--links',dest='links',default='http://imdb.com/find?s=all&q=,http://themoviedb.org/search?search=',help='comma-separated list of URIs of services to generate search links for, [default=%default]')
parser.add_option('-n','--names',dest='names',default='IMDB,MovieDB',help='coma-separated list of --links names, [default=%default]')
parser.add_option('-a','--anonymize',dest='anonymize',action='store_true',default=False,help='enable anonymous links via http://anonym.to [default=%default]')
parser.add_option('-t','--test',dest='test',action='store_true',default=False,help='generate testing sample results (-s is omitted) [default=%default]')
(options,args) = parser.parse_args()
if not os.path.exists(options.output):
	print 'Output dir %s does not exist! '%options.output
	sys.exit(1)
try:
	links =  options.links.split(',')
except:
	print 'Unable to parse --links argument'
	traceback.print_exc()
	sys.exit(1)
try:
	names = options.names.split(',')
except:
	print 'Unable to parse --names argument'
	traceback.print_exc()
	sys.exit(1)
if not len(names) == len(links):
	print '--links and --names must be comma-separated lists having same sizes'
	sys.exit(1)
if options.test:
	print 'Generating test results'
	reader = TestClient()	
else:
	reader = RPCClient(options.source,options.username,options.password)
print 'Getting movies'
movies = reader.get_movies()
if movies == None:
	sys.exit(0)
print 'Getting recently added'
recent_movies = reader.get_recently_added_movies()
print 'Getting shows'
tv_shows = reader.get_tv_shows()
#tv_shows = {}
generator = Generator(options.anonymize,names,links)
try:
	print 'Writing output to %s' % options.output
	f = open(options.output+'/index.html','w')
	movies = generator.parse_movies(movies)
	recent_movies = generator.parse_movies(recent_movies,sort=False)
	tv_shows = generator.parse_series(tv_shows)
	html = HTML % (datetime.datetime.now().strftime('%d. %m. %y at %H:%M:%S'),''.join(movies),''.join(recent_movies),''.join(tv_shows))
	f.write(html.encode('ascii','ignore'))
	print 'Done'
	print 'Copying resources'
	shutil.copy(RESOURCES+'/resources/sortable.js',options.output)
	shutil.copy(RESOURCES+'/resources/arrow-up.gif',options.output)
	shutil.copy(RESOURCES+'/resources/arrow-down.gif',options.output)
	shutil.copy(RESOURCES+'/resources/arrow-none.gif',options.output)
	shutil.copy(RESOURCES+'/resources/tabber.js',options.output)
	shutil.copy(RESOURCES+'/resources/tabber.css',options.output)
	shutil.copy(RESOURCES+'/resources/jquery.tools.js',options.output)
	print 'Done'
except:
	traceback.print_exc()
	sys.exit(1)
f.close()
