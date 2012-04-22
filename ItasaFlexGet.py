import urllib, urllib2, cookielib,urlparse
import os, random
from contextlib import closing
from BeautifulSoup import BeautifulSoup
import json

BASE_PATH = 'http://www.italiansubs.net/index.php'

class Itasa(object):

    """
    rss: http://www.italiansubs.net/index.php?option=com_rsssub...  #myitasa or itasa subtitle feed
    accept_all: yes  #accept all from myitasa                                               
    itasa:
      username: itasaUsername
      password: itasaPassword
      path: ~/subtitle/download/folder # absolute or starting from $HOME
      messages:
        - Grazie
        - Grazie mille!!!
        - Mitici
    """

    def validator(self):
        '''validator'''
        from flexget import validator
        d = validator.factory('dict')
        d.accept('text',key='username')
        d.accept('text',key='password')
        d.accept('text',key='path')
        return d

    def on_process_start(self, feed):
        '''Itasa login, storing cookie'''
        self.config = feed.config['itasa']

        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_data = urllib.urlencode({'username' : self.config['username']
                               , 'passwd' : self.config['password']
                               , 'Submit' :'Login'
                               , 'silent' : True
                               , 'option' : 'com_user'
                               , 'task'   : 'login'
                               , 'remember':'yes'})
        
        self.opener.open(BASE_PATH, login_data)

    def on_feed_download(self,feed):
        '''download zip file'''
        for entry in feed.entries:
            if entry.get('urls'):
                urls = entry.get('urls')
            else:
                urls = [entry['url']]
            for url in urls:
                with closing(self.opener.open(url)) as page:
                    z = self._zip(page)
                    filename = z.headers.dict['content-disposition'].split('=')[1]
                    filename = os.path.join(self.config['path'],filename)
                    filename = os.path.expanduser(filename)
                    with open(filename,'wb') as f:
                        f.write(z.read())
                    if 'messages' in self.config :
                        self._post_comment(page)

    def _zip(self,page):
        '''extract zip subtitle link from page, open download zip link'''
        content = page.read()
        start = content.index('<center><a href="')
        end = content.index('" rel',start)
        url = content[start+17:end]
        return self.opener.open(url)

    def _post_comment(self,page):
        soup = BeautifulSoup(page.read())
        form = soup.find(id='jc_commentForm')
        arg2_dict = []
        for inputTag in form.findAll('input'):
            if not inputTag['name'] == 'jc_name':
                arg2_dict.append([inputTag['name'],inputTag['value'] if inputTag.has_key('value') else None])

        m = self.config['messages']
        arg2_dict.append(['jc_comment',m[random.randint(0,len(m)-1)]  ])
        arg2_dict.append(['jc_name',self.config['username']])

        data = { 'arg2': json.dumps(arg2_dict)
            , 'func'   : "jcxAddComment"
            , 'task'   : "azrul_ajax"
            , 'no_html': 1
            , 'option' : "jomcomment"}
        
        return self.opener.open(page.geturl(),urllib.urlencode(data))

try:
    from flexget.plugin import register_plugin
    register_plugin(Itasa, 'itasa')
except:
    pass