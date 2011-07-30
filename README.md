xbmc-scripts
------------
is a set of simple python scripts, which can help you managing, tracking your movie library in XBMC

------------
### xbmc-export.py

generates single HTML page containing

 * all movies
 * recently added movies
 * tv shows

Main features:

 * tracks history of your library!!!
 * movies/series can be ordered (using javascript) by almost all columns
 * links to movie databases are generated too :-)

It requires jsonrpc API to be enabled on your XBMC instance

Take a look at sample output
http://jezzovo.net/xbmc-export-html-example/

Why to use this?

If you sometimes shutdown your XBMC box and you need to access your media library online, this is what you're looking for.
Script is intented to be a cron job to be up-to-date.
try : `python xbmc-export.py --help` to get more details

My setup: `xbmc-export.py -a -n MovieDB -l http://themoviedb.org/search?search= -s http://xbmcbox:8080/jsonrpc -u xbmc -p password -o /var/www/localhost/htdocs`

------------
### copy-recent-movies.py 

connects to XBMC via json-rpc and gets list of recently added movies and copies them to specified folder. 

It is required to run on same host as XBMC or to have data reachable the same way as XBMC does.

This is useful when you want to pick/backup your latest movies.

-------------
### movie-dups.py

connects to XBMC via json-rpc to get list of all movies in library. Checks if any movie is present more than once. This can help you not to have a mess in your library and save your disk space.
