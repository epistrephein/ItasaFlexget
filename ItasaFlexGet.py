#from __future__ import unicode_literals, division, absolute_import
import logging
from flexget import plugin
from flexget.event import event
import urllib, urllib2, cookielib, urlparse
import os, random, re
from contextlib import closing
from bs4 import BeautifulSoup
from flexget.utils.template import render_from_entry
import json

log = logging.getLogger('download')
BASE_PATH = 'http://www.italiansubs.net/index.php'

class Itasa(object):

    schema = {
        'oneOf': [
            {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
					'password': {'type': 'string'},
					'path': {'type': 'string', 'format': 'path'}
                },
                'additionalProperties': False
            },
        ]
    }
	
    def getToken(self, contentHtml):
        reg = re.compile('<input type="hidden" name="([a-zA-z0-9]{32})" value="1"')
        value = reg.search(contentHtml).group(1)
        return value
		
    def on_task_start(self, task, config):
        task.mock_output = []
        #self.config = task.config['itasa']

        cj = cookielib.CookieJar()
        #cj = cookielib.FileCookieJar('path_to_plugins\\coorkiejar')
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0'), ('Referer', BASE_PATH.rstrip('index.php'))]
        response = self.opener.open(BASE_PATH)
        content = response.read()
        token = self.getToken(content)
        login_data = urllib.urlencode({'username' : config.get('username')
                               , 'passwd' : config.get('password')
                               , 'Submit' :'Login'
                               , 'silent' : 'true'
                               , 'option' : 'com_user'
                               , 'task'   : 'login'
                               , token : '1'
                               , 'remember':'yes'})
        with closing(self.opener.open(BASE_PATH, login_data)) as page:
            #log.info(page.read().decode('utf-8'))
            if page.read().decode('utf-8').find('Nome utente e password non sono corrette') != -1:
                raise Exception("Wrong user or password")		

    def on_task_output(self, task, config):
        for entry in task.accepted:
            log.info('entry: %s' % entry)
            if entry.get('urls'):
                urls = entry.get('urls')
            else:
                urls = [entry['url']]
            for url in urls:                
                #log.info('url: %s' % url)
                with closing(self.opener.open(url)) as page:
                    try:
                        content = page.read()
                        z = self._zip(content)
                        filename = z.headers.dict['content-disposition'].split('=')[1]
                        path = config.get('path')
                        #log.info("configured path : %s", path)
                        path = render_from_entry(path, entry)
                        #log.info("rendered path : %s", path)
                        filename = os.path.join(path,filename)
                        filename = os.path.expanduser(filename)
                        soup = BeautifulSoup(content)
                        with open(filename,'wb') as f:
                            f.write(z.read())
                            entry['output'] = filename
                        #if 'messages' in self.config :
                        #    self._post_comment(soup,page.geturl())
                        self._fill_fields(entry,soup)    
                    except ValueError:
                        print("Missing subtitle link in page: %s" % page.geturl())  

    def _fill_fields(self,entry,soup):
        title = soup.find(id='remositoryfileinfo').find('center').string
        m = re.search("(.*?)[\s-]+(\d+)x(\d+)", title, re.UNICODE)
        if m:
            show_data = m.groups()
            entry['title'] = title.strip()
            entry['series_name'] = show_data[0].strip()
            entry['series_season'] = int(show_data[1].strip())
            entry['series_episode'] = int(show_data[2].strip())

    def _zip(self,content):
        '''extract zip subtitle link from page, open download zip link'''
        start = content.index('<center><a href="')
        end = content.index('" rel',start)
        url = content[start+17:end]
        return self.opener.open(url)
		
@event('plugin.register')
def register_plugin():
    plugin.register(Itasa, 'itasa', api_ver=2)

    
