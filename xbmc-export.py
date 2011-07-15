#!/bin/env python
# -*- coding: utf-8 -*-
RESOURCES=''


import urllib2,cookielib,base64,traceback,json,os,optparse,sys,datetime, shutil, client
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
		%s
	</div>
</body>
</html>
"""
HISTORY_TAB="""
<div class="tabbertab">
	<h2>Movie History</h2>
	<p>Here you can see, when some movie was added to library.</p>
	%s
</div>
"""
MOVIE="""
<tr class="%s">
	<td>%i</td>
	<td>%s</td>
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
DIFF_DIV="""
<div class="history">
	<h3>%s</h3>
	%s
	%s
</div>
"""
DIFF_TABLE="""
<table class="history">
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
"""

def update_fields(item,fields,default=''):
	for field in fields:
		if not field in item:
			item[field]=default
	return item
class HistoryGenerator(object):

	def __init__(self,output,movies,generator):
		time = datetime.datetime.now()
		self.output = output
		self.generator = generator
		self.snapshot=os.path.join(output,'movies.json')
		self.history_dir=os.path.join(output,'history')
		self.today = time.strftime('%d.%m %Y %H:%M:%S')
		self.current_diff=os.path.join(self.history_dir,time.strftime('%y-%m-%d-%H%M%S')+'.div')
		self.movies = self._create_dict(movies)
		self.snap_movies = {}

	def _create_dict(self,movies):
		dic = {}
		for movie in movies['movies']:
			dic[str(movie['movieid'])] = movie
		return dic
	def _create_list(self,movies):
		l = []
		for movie in movies:
			l.append(movies[movie])
		return l
	def _load_snapshot(self):
		if os.path.exists(self.snapshot):
			f = open(self.snapshot,'r')
			data = f.read()
			self.snap_movies = json.loads(unicode(data.decode('utf-8','ignore')))['movies']
			f.close()
	def _save_snapshot(self):
		f = open(self.snapshot,'w')
		f.write(json.dumps({'movies':self.snap_movies},ensure_ascii=True))
		f.close()

	def _create_diff_div(self,added,removed):
		added_content = ''
		removed_content = ''
		added = generator.parse_movies({'movies':self._create_list(added)},'history_added')
		removed = generator.parse_movies({'movies':self._create_list(removed)},'history_removed')
		if len(added)>0:
			added_content = DIFF_TABLE % (''.join(added))
		if len(removed)>0:
			removed_content = DIFF_TABLE % (''.join(removed))
		content = DIFF_DIV % (self.today,added_content,removed_content)
		f = open(self.current_diff,'w')
		f.write(content.encode('ascii','ignore'))
		f.close()
		return content
		
	def _create_diff(self):
		old = self.snap_movies
		new = self.movies
		added = {}
		removed = {}
		if old == {}:
			# snapshot was empty, returning nothing, since everythink would go do added
			return
		for key in old:
			if not key in new:
				removed[key] = old[key]
		for key in new:
			if not key in old:
				added[key] = new[key]
		if len(added)==0 and len(removed)==0:
			print ' Nothing has changed since last dump'
			return
		self._create_diff_div(added,removed)
		
	def _gather_diffs(self):
		contents = []
		for file in sorted(os.listdir(self.history_dir),reverse=True):
			if file.endswith('.div'):
				path = os.path.join(self.history_dir,file)
				f = open(path,'r')
				contents.append(f.read())
				f.close()
		return HISTORY_TAB % ''.join(contents)

	def generate(self):
		self._load_snapshot()
		if not os.path.exists(self.history_dir):
			os.mkdir(self.history_dir)
		self._create_diff()
		self.snap_movies = self.movies
		self._save_snapshot()
		return self._gather_diffs()

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

	def parse_movies(self,data,rowclass='',sort=True):
		movies = []
		if sort:
			data['movies'] = sorted(data['movies'],key=itemgetter('label'))
		for movie in data['movies']:
			movie = update_fields(movie,['year','genre','file','label','rating','duration'])
			movie = update_fields(movie,['playcount'],'0')
			movie['title'] = '<strong>%s</strong>' % movie['label']
			if int(movie['playcount'])>0:
				movie['title'] = '<i>%s</i>' % movie['label']
			movie['rating'] = '%.2f' % float(movie['rating'])
			movie['duration'] = '%i' % (int(movie['duration'])/60)
			m = MOVIE % (rowclass,len(movies)+1,movie['title'],self._get_links(movie['label']),movie['year'],movie['genre'],movie['rating'],movie['duration'],os.path.basename(movie['file']))
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
parser.add_option('-d','--diff',dest='history',action='store_true',default=True,help='enable history/diff tracking')
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
	reader = client.TestClient()	
else:
	reader = client.RPCClient(options.source,options.username,options.password)
print 'Getting movies'
movies = reader.get_movies()
if movies == None:
	sys.exit(0)
print 'Getting recently added'
recent_movies = reader.get_recently_added_movies()
print 'Getting shows'
tv_shows = reader.get_tv_shows()
generator = Generator(options.anonymize,names,links)
history = HistoryGenerator(options.output,movies,generator)
history_content=''
try:
	print 'Writing output to %s' % options.output
	f = open(options.output+'/index.html','w')
	movies = generator.parse_movies(movies)
	recent_movies = generator.parse_movies(recent_movies,sort=False)
	tv_shows = generator.parse_series(tv_shows)
	if options.history:
		print ' Generating history files'
		history_content = history.generate()
		print ' Done'
	html = HTML % (datetime.datetime.now().strftime('%d. %m. %y at %H:%M:%S'),''.join(movies),''.join(recent_movies),''.join(tv_shows),history_content)
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
