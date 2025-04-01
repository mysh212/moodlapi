from core.general import *

import requests
from bs4 import BeautifulSoup as bs

import json
from datetime import datetime

class moodle(dict):
    def __init__(self, session: str = None, rq: requests.Session = None):
        if rq: self.rq = rq
        elif session: self.rq = requests.Session(); self.rq.cookies.set('MoodleSession', session, domain = 'moodle.ncku.edu.tw')
        else: error('Neither session nor requests session were given.'); exit(-1)
        self.soup = None
        self.username = self.get_username().strip()
        self.logined = self.username is not None
        self.sync()
    
    def get_courses(this):
        url = 'https://moodle.ncku.edu.tw'
        if this.soup is None:
            html = this.rq.get(url)
            this.soup = bs(html.text, 'html.parser')
        soup = this.soup
        f = [i for i in soup.find_all('ul') if i.get('id', '').startswith('cat')][:-1]
        ans = []
        for i in f:
            ans += [[j.find('a').get('href', None) if j.find('a') is not None else None, j.text] for j in i.find_all('li')]
        courses = [course(*i[::-1], moodle = this) for i in ans]
        return courses
    
    def __str__(this):
        session = this.rq.cookies.get('MoodleSession')
        return f'Moodle Session: {session}\nUsername: {this.username}'
    
    def check_logined(this):
        url = f'https://moodle.ncku.edu.tw/lib/ajax/service.php'
        junk = this.rq.post(url, data = '''[{"index":0,"methodname":"core_fetch_notifications","args":{"contextid":1}}]''')
        debug(json.loads(junk.text)[0])
        this.logined = (not json.loads(junk.text)[0].get('error', True))
        return this.logined
    
    def get_username(this):
        url = 'https://moodle.ncku.edu.tw'
        now = bs(this.rq.get(url).text, 'html.parser').find('span', class_ = 'userbutton')
        if now is not None: return now.text;
        else: return None;

    def sync(this):
        super().__init__(username = this.username, logined = this.logined)

class course(dict):
    def __init__(self, name, url, session: str = None, moodle: moodle = None, rq: requests.Session = None):
        self.name = name
        self.url = url
        if self.url is not None: self.enabled = True
        else: self.enabled = False
        if moodle is not None: self.rq = moodle.rq; self.moodle = moodle
        elif rq: self.rq = rq
        elif session: self.rq = requests.Session(); self.rq.cookies.set(MoodleSession, session, domain = 'moodle.ncku.edu.tw')
        else: error('Neither session nor requests session were given.'); exit(-1)
        self.sync()

    def init(this, x):
        this.name = x.name
        this.url = x.url
        this.enabled = x.enabled
        this.rq = x.rq

    def sync(this):
        super().__init__(name = this.name, url = this.url)

    def __str__(self):
        if self.enabled:
            return f'Name: {self.name}\nURL: {self.url}'
        else:
            return f'Name: {self.name}'
        
    def get_course_html(self):
        if not self.enabled: return None
        return self.rq.get(self.url).text
    
    def get_contents(this):
        html = this.get_course_html()
        if not html: return [];
        ans = []
        for i in bs(html, 'html.parser').find_all('div', class_ = 'content'):
            if i.find('h3', class_ = 'sectionname') is None: continue;
            title = i.find('h3', class_ = 'sectionname').text
            content = []
            for i in i.find_all('li'):
                content.append(resource(this, i.text, i, (lambda x: x[0] if len(x) > 0 else None)([i for i in i.get('class', []) if i.startswith('modtype')]), i.find('a').get('href') if i.find('a') is not None else None))
                # if i.get('class', None) is None or 'modtype_label' in i.get('class', None) or i.find('a') is None:
                #     continue
                # content.append([i.find('a').get('href'), i.text])
            ans.append(section(this, title, content))
        return ans
    
    # def __dict__
    
class section(dict):
    def __init__(this, course: course, name: str, content: list):
        this.course = course
        this.name = name
        this.content = content
        this.sync()
    
    def sync(this):
        super().__init__(name = this.name, content = this.content)

    def __str__(this):
        return f'Section Name: {this.name}\n' + '\n'.join([str(i) for i in this.content])
    
    def init(this):
        for i in range(len(this.content)):
            ans = this.content[i].auto()
            if ans == False: continue;
            ans.init()
            this.content[i] = ans
        return this
    
class resource(dict):
    def __init__(this, course: course, name: str, html: bs, type = 'modtype_label', url = None):
        this.course = course
        this.name = name
        this.url = url
        this.html = html
        this.type = type
        this.content = None
        this.sync()

    def copy(this, x):
        this.course = x.course
        this.name = x.name
        this.url = x.url
        this.html = x.html
        this.type = x.type
        this.sync()

    def sync(this):
        super().__init__(name = this.name, type = this.type, url = this.url, content = this.content)

    def auto(this):
        if this.type == 'modtype_forum':
            return discuss(this)
        return False
    
    def set_content(this, x):
        this.content = x
        this.sync()
    
    def init(this):
        return this

    def __str__(this):
        return f'Name: {this.name}\nType: {this.type}\nURL: {this.url}'
    
class discuss(resource):
    class content(dict):
        def __init__(this, discuss, url, name):
            this.discuss = discuss
            this.url = url
            this.name = name
            this.title = None
            this.content = None
            this.user = None
            this.time = None
            this.sync()

        def sync(this):
            super().__init__(url = this.url, name = this.name, title = this.title, content = str(this.content) if this.content is not None else None, user = this.user, time = str(this.time) if this.time is not None else None)

        def __str__(this):
            return f'user: {this.user}\ntime: {this.time}\nURL: {this.url}\nname: {this.name}\ntitle: {this.title}'
        
        def get_content(this):
            html = this.discuss.course.rq.get(this.url).text
            soup = bs(html, 'html.parser')
            header = soup.find(class_ = 'd-flex flex-column')
            this.user = header.find('a').text.strip()
            this.time = datetime.strptime(header.find('time').text, '%Y年 %m月 %d日(%a) %H:%M')
            this.title = header.find('h3').text
            this.content = soup.find('div', class_ = 'no-overflow w-100 content-alignment-container').find('div')
            this.sync()
            return this

    def __init__(this, resource: resource):
        if resource.type != 'modtype_forum':
            warning('Converting resource which is not discuss into it.')
        super().copy(resource)
        this.topic = None

    def get_topics(this):
        if this.topic is not None: return this.topic;
        this.topic = [discuss.content(this, i.find('a').get('href', None), i.find('a').text.strip()) if i.find('a') is not None else None for i in bs(this.course.rq.get(this.url).text, 'html.parser').find_all('th', class_ = 'topic')]
        super().set_content(this.topic)
        return this.topic
    
    def init(this):
        ans = this.get_topics()
        # for i in range(len(ans)):
        #     ans[i].get_content()
        super().set_content(ans)
        # this.topic = ans
        return ans
    
    # def get_content(this, index: int):
    #     if len(this.topic) == 0:
    #         this.get_topic()
    #     if not 0 <= index < len(this.topic):
    #         error('Invalid index getting content of a discuss thread')
    #         return None
        