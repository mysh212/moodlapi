from core.general import *

import json
from matplotlib import pyplot as plt

import requests
from bs4 import BeautifulSoup as bs

import cv2
import pytesseract as pt

headers = dict([i.split(': ') for i in '''Host: moodle.ncku.edu.tw
# Content-Length: 100
Cache-Control: max-age=0
Sec-Ch-Ua: "Chromium";v="131", "Not_A Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Accept-Language: zh-TW,zh;q=0.9
Origin: https://moodle.ncku.edu.tw
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'''.split('\n') if not i.startswith('#')])

root = 'https://moodle.ncku.edu.tw'

class login:
    def __init__(self, username, password):
        self.soup = ''
        self.username = username
        self.password = password

    def get_login(self):
        url = f'{root}/login/index.php'
        self.req = requests.get(url, headers = headers)
        self.html = self.req.text
        self.soup = bs(self.html, 'html.parser')
        return self.req, self.soup

    def get_token(self) -> str:
        soup = self.soup

        self.login_token = soup.select_one('input[name=logintoken]')['value']
        debug(self.login_token)
        return self.login_token

    def get_session(self) -> str:
        req = self.req

        cookies = dict([i.split('=') for i in req.headers['Set-Cookie'].split('; ')])

        self.session = cookies['MoodleSession']
        debug(self.session)
        return self.session

    def get_login_key(self) -> str:
        req = self.req
        html = req.text
        key = [i for i in html.split('\n') if i.find('M.cfg') != -1][0]
        key = key[key.find('{') + 1:key.find('}')]
        key = dict([[j[1:-1] for j in i.split(':', 1)] for i in key.split(',')])
        key = key['sesskey']
        debug(key)
        self.key = key
        return key
    
    def send_junk(self):
        session = self.session
        junk = requests.post(f'{root}/lib/ajax/service.php?sesskey={self.key}&info=core_fetch_notifications', cookies = {
            'MoodleSession': session
        }, data = '''[{"index":0,"methodname":"core_fetch_notifications","args":{"contextid":1}}]''', headers = headers)
        debug(json.loads(junk.text))
    
    def get_captcha(self):
        soup = self.soup
        session = self.session
        
        captcha = soup.find('img', id = 'imgcode')['src']
        debug(captcha)
        open('captcha.png', 'wb').write(requests.get(captcha, cookies = {
            'MoodleSession': session
        }).content)
        self.img = cv2.imread('captcha.png')
        return cv2.imread('captcha.png')
    
    def parse_img(self):
        img = self.img
        xx = [0,1,0,-1,1,-1,1,-1]
        yy = [1,0,-1,0,1,1,-1,-1]

        white = img[1][1]
        nimg = img.copy()
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                ans = 0
                for k in range(8):
                    nx = i + xx[k]
                    ny = j + yy[k]
                    if nx < 0 or ny < 0 or nx >= img.shape[0] or ny >= img.shape[1]: continue;
                    if (img[nx][ny] == img[i][j]).all(): ans = ans + 1
                if ans >= 2:
                    continue
                nimg[i][j] = white

        self.nimg = nimg[1:nimg.shape[0] - 1, 1:nimg.shape[1] - 1]
        return self.nimg
    
    def get_code(self):
        img, nimg = self.img, self.nimg

        # pt.pytesseract.tesseract_cmd = r'C:\Users\ysh00\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        def get_code(i) -> str:
            ans = pt.image_to_string(i, config = 'digits')
            ans = ''.join([i for i in ans if i.isdigit()])
            return ans

        self.code = [get_code(i) for i in [img, nimg]]

        debug(self.code)

        return self.code

        # ans
    
    def login(self):
        username = self.username
        password = self.password
        code = self.code[1]
        login_token = self.login_token
        session = self.session

        self.pre = requests.post(f'{root}/login/index.php', data = {
            'anchor': '',
            'logintoken': login_token,
            'username': username,
            'password': password,
            'vcode': code
        }, cookies = {
            'MoodleSession': session
        }, headers = headers, allow_redirects = False)
        del self.password
        try:
            self.session = dict([i.split('=', 1) for i in self.pre.headers['Set-Cookie'].split('; ')])['MoodleSession']
            debug(self.session)
            # now = requests.get(f'{root}', cookies = {
            #     'MoodleSession': session
            # }, headers = headers).text
        except:
            warning('Ignoring new token')
            pass
        return self.pre
    
    def try_check_login(self):
        pre = self.pre
        session = self.session

        self.pre = requests.get(pre.headers['Location'], cookies = {
            'MoodleSession': session
        }, headers = headers)
        return self.pre
    
    def check_login(self):
        pre, session = self.pre, self.session

        ns = bs(pre.text, 'html.parser')
        if len(ns.find_all('a', id = 'loginerrormessage')) >= 1:
            message = ns.find('a', id = 'loginerrormessage').text
            error(message)
            self.error = message
            return False
        else:
            info('========== Final Token ==========')
            info(f'{session:^33}')
        return True
    
    def auto(self):
        self.get_login()
        self.get_token()
        self.get_session()
        self.get_login_key()
        self.send_junk()
        self.get_captcha()
        self.parse_img()
        self.get_code()
        self.login()
        self.try_check_login()
        return self.check_login()
    
if __name__ == '__main__':
    t = moodle()
    t.get_login()
    t.get_token()
    t.get_session()
    t.get_login_key()
    t.send_junk()
    t.get_captcha()
    t.parse_img()
    t.get_code()
    t.login()
    t.try_check_login()
    info(t.check_login())
